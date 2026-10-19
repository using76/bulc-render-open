"""Render one BUL:BIT basic-mode frame (fire from hrrpuv, smoke from smoke_sigma) to a PNG image.

    set BULBIT_HOME=C:\\BULBIT                       (the unzipped release; default: the folder above this script)
    python examples\\render_basic_frame.py iso9705_200kw_nvdb 20.0 fire_20s.png
    python examples\\render_basic_frame.py iso9705_200kw_nvdb 20.0 fire_20s.png --eye 3.2 -2.5 1.4 --target 1.4 1.2 1.0

Needs Python 3.10+ with numpy, scipy and torch (CUDA). The Python of Isaac Sim / Isaac Lab has all three.
The renderer draws the fire volume only (flame and smoke); it does not know walls or floors. Walls are drawn by your
engine (Isaac Sim, your own renderer); pass its depth buffer to Renderer.render(depth=...) so the fire is cut by them.
"""
import argparse
import os
import struct
import sys
import zlib

import numpy as np

HOME = os.environ.get("BULBIT_HOME") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("BULBIT_DLL", os.path.join(HOME, "bin", "bulbit.dll"))
sys.path.insert(0, os.path.join(HOME, "python"))

import torch  # noqa: E402

import bulbit  # noqa: E402
from bulbit import Lattice, camera_look_at  # noqa: E402
from bulbit.look import Look, ramps_v0  # noqa: E402
from bulbit.scene import lights_from_flame  # noqa: E402
from bulbit_basic import frames, hrr_flame  # noqa: E402


def write_png(path, rgb):
    """rgb: uint8 (H, W, 3), rows top-down. A plain PNG writer (zlib only)."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("nvdb_dir", help="the <CHID>_nvdb folder written by bulbit_sim")
    ap.add_argument("t", type=float, help="simulation time [s] of the frame")
    ap.add_argument("out", help="output PNG")
    ap.add_argument("--eye", type=float, nargs=3, help="camera position [m] (default: in front of the fire)")
    ap.add_argument("--target", type=float, nargs=3, help="point the camera looks at [m] (default: the flame centre)")
    ap.add_argument("--size", type=int, nargs=2, default=(960, 540), metavar=("W", "H"))
    ap.add_argument("--hfov", type=float, default=60.0, help="horizontal field of view [deg]")
    a = ap.parse_args()

    man = frames.read_manifest(a.nvdb_dir)
    files = frames.frame_files(a.nvdb_dir, man)
    try:
        k = frames.frame_of_key(man, a.t)
    except frames.BitError as e:
        raise SystemExit("%s; frames are every %g s from t = %g s" % (e, man["frame_dt"], man["t_begin"]))
    if k not in files:
        raise SystemExit("no frame for t = %g s in %s (frames %d .. %d, every %g s)"
                         % (a.t, a.nvdb_dir, min(files), max(files), man["frame_dt"]))
    fr = frames.load_frame(files[k], man)
    sigma_lat = Lattice(fr["origin"], fr["spacing"], fr["shape"])

    # flame field from the heat release rate (the BUL:BIT basic-mode rule, bulbit_basic/hrr_flame.py)
    if fr["hrrpuv"] is not None:
        F, f_origin = hrr_flame.flame_from_hrr(fr["hrrpuv"], fr["origin"], fr["spacing"])
    else:
        F, f_origin = np.zeros(hrr_flame.EMPTY_SHAPE, np.float32), fr["origin"]
    v = hrr_flame.VOXEL_M
    flame_lat = Lattice(f_origin, (v, v, v), F.shape)

    look, ramps = Look.v1(1.0), ramps_v0()
    lights = lights_from_flame(flame_lat, F, Look.v0(), ramps, k=8)     # point lights that light the smoke

    # camera: by default 4 m in front of the flame centre (or of the domain centre when nothing burns)
    if a.target is not None:
        target = tuple(a.target)
    elif F.any():
        idx = np.argwhere(F > 0.1) if (F > 0.1).any() else np.argwhere(F > 0)
        target = tuple(float(f_origin[i] + (idx[:, i].mean() + 0.5) * v) for i in range(3))
    else:
        target = tuple(float(fr["origin"][i] + 0.5 * fr["shape"][i] * fr["spacing"][i]) for i in range(3))
    eye = tuple(a.eye) if a.eye is not None else (target[0], target[1] - 4.0, target[2] + 0.5)
    W, H = a.size
    cam = camera_look_at(eye, target, W, H, a.hfov)

    r = bulbit.Renderer(mode="primary")          # shares the CUDA context with torch (and Isaac Sim)
    r.set_sigma(sigma_lat, torch.from_numpy(fr["sigma"]).cuda())
    r.set_flame(flame_lat, torch.from_numpy(F).cuda())
    r.set_look(look)
    r.set_ramps(*ramps)
    r.set_lights(lights)

    bg = torch.full((1, H, W, 4), 60, dtype=torch.uint8, device="cuda")        # the background image (grey)
    bg[..., 3] = 255
    depth = torch.full((1, H, W), 1.0e4, dtype=torch.float32, device="cuda")   # no geometry in front of the fire
    out = torch.zeros_like(bg)
    r.render([cam], W, H, depth=depth, download=False)
    r.composite(bg=bg, out=out)
    r.sync()
    write_png(a.out, out[0, :, :, :3].cpu().numpy())
    r.close()
    print("t = %.1f s (frame %d): hrrpuv max %.0f kW/m3, smoke_sigma max %.2f 1/m, %d lights -> %s"
          % (a.t, k, float(fr["hrrpuv"].max()) if fr["hrrpuv"] is not None else 0.0, float(fr["sigma"].max()),
             len(lights), a.out))


if __name__ == "__main__":
    main()
