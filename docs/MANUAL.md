# BUL:BIT 사용설명서

BUL:BIT(불빛) 0.91.0, 기본 모드. 2026-10-23.

**0.91.0에서 새로 생긴 것:** 불꽃 세부(FX). Mantaflow 불꽃처럼 깜빡이고 작게 흔들리는 불꽃을 BUL:C 계산의 열방출률로
만듭니다(6.5절). 계산 코어 `bulbit_sim`은 0.90.0과 같습니다(실행 화면의 버전 표기도 0.90.0).

> BUL:C computes the fire. BUL:BIT renders it. — 불씨(BUL:C)가 불을 계산하고, 불빛(BUL:BIT)이 그 불을 그린다.

---

## 1. BUL:BIT란

BUL:BIT는 **화재 렌더러**입니다. 화재 시뮬레이터 BUL:C(불씨)의 GPU 코어로 계산한 불꽃과 연기를 영상, 게임 엔진, 로봇
시뮬레이터(NVIDIA Isaac Sim)의 카메라 화면으로 그립니다.

| 구성 | 파일 | 하는 일 |
|---|---|---|
| 계산 코어 | `bin/bulbit_sim.exe` | FDS 형식의 화재 입력(`.fds`)을 GPU로 계산하고, 렌더용 NanoVDB 프레임만 씁니다 |
| 렌더 라이브러리 | `bin/bulbit.dll`, `include/bulbit.h` | 연기와 불꽃 볼륨을 카메라 영상으로 그립니다(CUDA). C ABI |
| Python 패키지 | `python/bulbit` | `bulbit.dll`의 Python 바인딩. torch·Warp·CuPy의 CUDA 배열을 복사 없이 받습니다. 불꽃 세부는 `bulbit.fx`(0.91.0부터) |
| 프레임 도구 | `python/bulbit_basic` | NanoVDB 프레임 읽기(`frames`), 열방출률로 불꽃 만들기(`hrr_flame`) |
| 예제 | `examples/` | ISO 9705 방 화재 입력, 프레임 한 장을 그리는 스크립트, 불꽃 세부 영상을 만드는 스크립트 |

**기본 모드.** 지금 열려 있는 기능은 기본 모드뿐입니다. 프레임마다 세 가지 값을 내보내고, 그것으로 불꽃과 연기를 그립니다.

| 값 | 이름 | 단위 | 그리는 것 |
|---|---|---|---|
| 그을음 소광계수 (soot) | `smoke_sigma` | 1/m | 연기 |
| 열방출률 (HRR) | `hrrpuv` | kW/m³ | 불꽃 |
| 시야 (visibility) | `visibility` | m | 시야 판정(= min(30, 3 / smoke_sigma)) |

Pro 기능(온도, 속도, CO, CO₂, 압력, 열화상 등)은 잠겨 있습니다.

**BUL:BIT는 공학 해석 도구가 아닙니다.** `bulbit_sim`은 측정점, CSV, 슬라이스, 경계 파일 같은 공학 출력을 쓰지 않습니다.
화재 안전 설계와 성능 위주 설계에는 BUL:C를 쓰십시오.

---

## 2. 필요한 것

| 항목 | 조건 |
|---|---|
| 운영체제 | Windows 10 또는 11, 64비트 |
| GPU | NVIDIA, 연산 능력(compute capability) 8.6 이상: GeForce RTX 30·40·50 계열, RTX A·Ada 계열 워크스테이션 GPU. A100(8.0)은 이 빌드로 돌지 않습니다 |
| 드라이버 | CUDA 13.1 이상을 지원하는 NVIDIA 드라이버. 확인한 조합: RTX 5070 Ti, 드라이버 610.88 |
| GPU 메모리 | 격자에 따라 다릅니다. 셀 51만 개(200×160×16) 계산이 16 GB GPU에서 돌았습니다 |
| 디스크 | 프레임 한 장이 셀 51만 개에서 약 3.6 MB입니다(0.1 s 간격이면 100 s에 약 3.6 GB) |
| 계정 | BUL:C 계정(로그인에 씁니다). https://bulc.msimul.com |
| 인터넷 | 로그인할 때만 필요합니다. 그 뒤 15일 동안은 오프라인으로 돕니다 |
| Python (렌더할 때) | Python 3.10 이상과 `numpy`, `scipy`, `torch`(CUDA). Isaac Sim·Isaac Lab의 Python에는 모두 들어 있습니다 |

---

## 3. 설치

1. GitHub의 [Releases](https://github.com/using76/bulc-render-open/releases)에서 `bulbit-0.91.0-win64.zip`을 받습니다.
2. 원하는 곳에 풉니다. 이 설명서에서는 `C:\BULBIT`이라고 합니다.

```
C:\BULBIT\
  bin\        bulbit_sim.exe  bulbit.dll  cufft64_12.dll
  include\    bulbit.h
  python\     bulbit\  bulbit_basic\
  spec\       look_v0.json  look_v1.json  look_v2.json
  examples\   iso9705_200kw.fds  render_basic_frame.py  render_fx_video.py
  docs\       MANUAL.md
  LICENSE.md  THIRD_PARTY_NOTICES.md
```

- `cufft64_12.dll`은 `bulbit_sim.exe`와 같은 폴더에 두어야 합니다(NVIDIA cuFFT, `THIRD_PARTY_NOTICES.md`).
- 설치 프로그램이나 레지스트리 등록은 없습니다. 지울 때는 폴더를 지우면 됩니다(로그인 기록은 4.4절).

---

## 4. 로그인과 이용 조건

### 4.1 로그인

```bat
C:\BULBIT\bin\bulbit_sim.exe login
```

1. 이용 조건(한국어·영어)이 먼저 나옵니다.
2. 기본 브라우저가 열립니다. BUL:C 계정으로 로그인합니다. 브라우저가 열리지 않으면 화면에 찍힌 주소를 직접 엽니다.
3. 브라우저에 "BUL:BIT 로그인 성공"이 나오면 탭을 닫습니다. 터미널에 계정과 무료 이용 기간이 나옵니다.

```
 BUL:BIT 로그인 완료 (signed in).
 계정 (account): you@example.com
 무료 이용 기간 (free pass): 2026-10-20 09:00 ~ 2026-11-04 09:00 (남은 기간 15일, 15 day(s) left)
```

- 로그인은 5분 안에 끝내야 합니다.
- 로그인하는 동안 이 PC의 `localhost:9876`에서 브라우저의 응답을 받습니다. 방화벽이 이 주소를 막으면 로그인이 끝나지 않습니다.
- 인터넷 연결은 Windows의 프록시 설정을 따릅니다.
- "이 BUL:C 라이선스를 다른 곳에서 쓰고 있습니다"가 나오면, 그 세션을 끝내고 이 PC에서 쓰려면 `bulbit_sim login --replace`.

### 4.2 이용 조건 (15일 무료 이용권)

- 이 PC에서 **처음 로그인한 때부터 15일** 동안 쓸 수 있습니다. 로그아웃하거나 다시 로그인해도 기간은 처음 로그인한 때부터 셉니다.
- **연구와 교육 목적으로만** 쓸 수 있습니다. **상업적 용도로는 쓸 수 없습니다.**
- 15일이 지난 뒤에도 쓰려면 문의 바랍니다: **simul@msimul.com**, **https://bulc.msimul.com**
- 전체 조건은 `LICENSE.md`에 있습니다.

### 4.3 상태 보기와 로그아웃

```bat
C:\BULBIT\bin\bulbit_sim.exe license     :: 이용 조건, 계정, 남은 기간
C:\BULBIT\bin\bulbit_sim.exe logout      :: 이 PC의 로그인 정보를 지웁니다 (기간은 이어서 셉니다)
```

계산을 시작할 때마다 첫머리에 남은 기간이 한 줄 나옵니다.

```
 License: OK. BUL:BIT 무료 이용권(연구·교육용, 상업적 사용 불가): 2026-11-04 09:00까지, 남은 기간 12일 ...
```

### 4.4 이 PC에 남는 것

- 로그인 기록: `%APPDATA%\BULC\bulbit-license.bin`. Windows 사용자 계정에 묶어 암호화합니다. 다른 PC로 옮기면 쓸 수 없습니다.
- 무료 이용 기간의 시작 날짜는 레지스트리(현재 사용자)와 ProgramData 폴더에도 암호화해 둡니다. 그래서 로그인 기록을 지우거나
  같은 PC의 다른 Windows 계정으로 로그인해도 기간은 처음 로그인한 날부터 셉니다.
- 이 기록들을 고치거나 옮기거나, 기간을 늘리려고 지우는 것은 이용 조건 위반입니다.

---

## 5. 화재 계산 (`bulbit_sim`)

### 5.1 실행

```bat
cd C:\work\iso9705
copy C:\BULBIT\examples\iso9705_200kw.fds .
C:\BULBIT\bin\bulbit_sim.exe iso9705_200kw.fds > run.log 2>&1
```

- **출력은 파일로 보내십시오**(`> run.log 2>&1`). 출력을 도중에 닫히는 파이프로 보내면(예: `| more`를 끝내기 전에 닫음)
  계산이 멈춥니다.
- `-fast`: 빠른 모드(FFT 압력해 + 간이 복사, 약 1.6배 빠름). 기본은 정밀 모드입니다.
- 걸리는 시간의 예: 셀 51만 개, 100 s 계산이 RTX 5070 Ti에서 약 4분 20초.

### 5.2 입력

- FDS 6 형식의 입력 파일(`.fds`)을 읽습니다. 받는 입력의 범위는 BUL:C GPU 코어와 같습니다.
  - 형상: `&MESH`, `&OBST`, `&HOLE`, `&VENT`.
  - 화원과 연소: `&SURF`(`HRRPUA` 등), `&REAC`(`SOOT_YIELD`가 연기의 양을 정합니다).
  - 시간: `&TIME T_END`.
- 공학 출력 줄(`&DEVC`, `&SLCF`, `&BNDF` 등)은 읽기는 하지만 아무 파일도 쓰지 않습니다.
- 측정점과 제어(`&DEVC`, `&CTRL`)로 문·장애물·벤트를 열고 닫는 것은 됩니다. 측정점 값으로 계산을 끝내는 `CTRL KILL`은 막혀 있습니다.
- `--restart`(이어서 계산)는 없습니다.

### 5.3 출력: NanoVDB 프레임

계산을 돌린 폴더에 `<CHID>_nvdb\`가 생깁니다.

```
iso9705_200kw_nvdb\
  manifest.json               격자, 프레임 간격, 채널 목록과 단위
  iso9705_200kw_0001.nvdb     t = 0.0 s
  iso9705_200kw_0002.nvdb     t = 0.1 s
  ...
```

- 프레임 n은 t = t_begin + (n − 1) × 0.1 s의 상태입니다. 간격은 환경 변수 `BULBIT_FRAME_DT`(초)로 바꿉니다. 한 시간 단계가
  여러 프레임 칸을 건너뛰면 그 칸의 파일은 없습니다.
- 프레임마다 float 격자 세 개가 이 순서로 들어 있습니다.

| 격자 | 단위 | 배경값 | 활성 문턱 | 정의 |
|---|---|---|---|---|
| `smoke_sigma` | 1/m | 0 | 0.001 | 8700 m²/kg × 그을음 밀도 × (1 − smoothstep(400 ℃, 600 ℃, T)). 고체 셀은 0 |
| `hrrpuv` | kW/m³ | 0 | 1 | 단위 부피당 열방출률(BUL:C의 HRRPUV와 같은 값) |
| `visibility` | m | 그 프레임의 최댓값 | 0.5 | min(30, 3 / smoke_sigma). smoke_sigma가 0이면 30 |

- `smoke_sigma`의 온도 항은 불꽃 속(400~600 ℃ 이상)의 연기를 뺍니다. 그 자리는 `hrrpuv`로 그린 불꽃이 채웁니다.
- 격자 좌표: 원점은 셀 (0, 0, 0)의 낮은 모서리이고, 간격은 `manifest.json`의 `mesh`(dx, dy, dz)입니다.
- 프레임 합계 확인: Σ `hrrpuv` × 셀 부피는 그 시각의 전체 열방출률(kW)입니다.
- Python에서는 `bulbit_basic.frames`로 읽습니다(6절).

### 5.4 종료 코드

| 코드 | 뜻 | 할 일 |
|---|---|---|
| 0 | 성공 | |
| 1 | 입력 오류, GPU 오류, 계산 실패 | `run.log`의 `ERROR`와 힌트 줄을 봅니다(8절) |
| 3 | 라이선스: 로그인하지 않음, 로그아웃, 기록 오류, 시계 이상 | `bulbit_sim login` |
| 4 | 15일 무료 이용 기간이 끝남 | 문의: simul@msimul.com, https://bulc.msimul.com |

---

## 6. 렌더 (Python)

### 6.1 준비

```bat
set BULBIT_HOME=C:\BULBIT
set BULBIT_DLL=C:\BULBIT\bin\bulbit.dll
set PYTHONPATH=C:\BULBIT\python
```

예제 스크립트는 `BULBIT_HOME`만 있으면 나머지를 스스로 맞춥니다.

### 6.2 프레임 한 장 그리기 (예제)

```bat
python C:\BULBIT\examples\render_basic_frame.py iso9705_200kw_nvdb 20.0 fire_20s.png
python C:\BULBIT\examples\render_basic_frame.py iso9705_200kw_nvdb 20.0 fire_20s.png --eye 3.2 -2.5 1.4 --target 1.4 1.2 1.0
```

20 s 프레임의 불꽃과 연기를 960×540 PNG로 그립니다. 카메라 위치(`--eye`)와 보는 점(`--target`)은 m 단위의 계산 좌표입니다.
주지 않으면 불꽃 중심 앞 4 m에서 봅니다. 렌더러는 불과 연기 볼륨만 그리고 벽이나 바닥은 그리지 않습니다(6.4절).

### 6.3 스크립트에서 쓰기

```python
import torch, bulbit
from bulbit import Lattice, camera_look_at
from bulbit.look import Look, ramps_v0
from bulbit.scene import lights_from_flame
from bulbit_basic import frames, hrr_flame

man = frames.read_manifest("iso9705_200kw_nvdb")
files = frames.frame_files("iso9705_200kw_nvdb", man)
fr = frames.load_frame(files[frames.frame_of_key(man, 20.0)], man)   # sigma, hrrpuv, visibility, origin, spacing, shape

F, f_origin = hrr_flame.flame_from_hrr(fr["hrrpuv"], fr["origin"], fr["spacing"])   # 불꽃 장 F (0..1), 0.1 m 격자
v = hrr_flame.VOXEL_M
smoke_lat, flame_lat = Lattice(fr["origin"], fr["spacing"], fr["shape"]), Lattice(f_origin, (v, v, v), F.shape)

r = bulbit.Renderer(mode="primary")                 # torch(그리고 Isaac Sim)와 CUDA 문맥을 함께 씁니다
r.set_sigma(smoke_lat, torch.from_numpy(fr["sigma"]).cuda())
r.set_flame(flame_lat, torch.from_numpy(F).cuda())
look, ramps = Look.v1(1.0), ramps_v0()
r.set_look(look); r.set_ramps(*ramps)
r.set_lights(lights_from_flame(flame_lat, F, Look.v0(), ramps, k=8))   # 불빛이 연기를 비추는 점광원

cam = camera_look_at((1.4, -2.8, 1.5), (1.4, 1.2, 1.0), 960, 540, 60.0)
bg = torch.full((1, 540, 960, 4), 60, dtype=torch.uint8, device="cuda"); bg[..., 3] = 255
depth = torch.full((1, 540, 960), 1e4, dtype=torch.float32, device="cuda")
out = torch.zeros_like(bg)
r.render([cam], 960, 540, depth=depth, download=False)   # L(빛), T(투과율), Z
r.composite(bg=bg, out=out)                                 # out = L + T × 배경
r.sync()
```

- **불꽃 규칙** (`hrr_flame`): `hrrpuv`를 0.1 m 격자로 삼선형 보간하고 0.05 m 가우시안을 건 값 q로
  F = clip(ln(q / 200) / ln(10000 / 200), 0, 1). 200 kW/m³ 이하는 불꽃이 아닙니다(Smokeview의 기본 불꽃 문턱).
- **연기**: `smoke_sigma`를 그대로 소광계수로 씁니다.
- 입력 배열은 numpy(복사) 또는 CUDA 배열(복사 없이 빌려 씀, `__cuda_array_interface__`)입니다. `mode="own"`이면 numpy만 받습니다.
- `Renderer.render(cams, w, h, depth, out, stream, download)`: 카메라 여러 대를 한 번에 그립니다.
  `depth`는 엔진의 깊이 버퍼(m, CUDA float32)로, 그 앞의 불과 연기만 그립니다.
- `Renderer.composite(bg, out, exposure, tonemap)`: 엔진 영상(CUDA uint8, RGB 또는 RGBA) 위에 불과 연기를 얹습니다.
  `tonemap`은 `"none"`(기본), `"aces"`, `"shoulder"`.
- 보는 방식(Look): `Look.v0()`, `Look.v1(1.0)`(불꽃 단계가 촘촘함), `Look.v2(1.0)`(부드러운 불꽃 재구성). 값은 `spec/look_v*.json`에 있습니다.

### 6.4 Isaac Sim에서 쓰기

Isaac Sim이나 Isaac Lab의 Python에서 `bulbit`을 불러 카메라마다 불과 연기를 합성합니다.

1. Isaac Sim을 띄우기 전에 `BULBIT_DLL`과 `PYTHONPATH`를 6.1절처럼 맞춥니다.
2. `bulbit.Renderer(mode="primary")`는 Isaac Sim·torch와 같은 CUDA 문맥을 씁니다. 렌더 결과는 GPU 안에서 그대로 합성됩니다.
3. 카메라: `bulbit.camera_from_usd(m, focal_mm, h_aperture_mm, W, H)`. `m`은 USD 카메라 프림의 월드 변환(4×4, USD 행벡터
   규약), `focal_mm`과 `h_aperture_mm`은 카메라의 초점 거리와 가로 조리개입니다. 화재 좌표를 월드에 옮길 때는 `bulbit.shift_cameras`.
4. 카메라 영상이 나올 때마다: `render(cams, W, H, depth=카메라 깊이)` → `composite(bg=카메라 RGB)`. 깊이를 주면 로봇, 차, 벽 뒤의
   불과 연기는 가려집니다.
5. 시간에 따라 프레임을 바꿀 때는 `set_sigma`, `set_flame`, `set_lights`를 다시 부릅니다. 프레임 읽기와 불꽃 만들기는 CPU에서
   1초 안팎이 걸리므로, 학습처럼 많이 돌릴 때는 미리 만들어 두고 읽어 쓰기를 권합니다.

- 시야(`visibility`)와 연기 투과율은 로봇이 연기 너머를 볼 수 있는지 판정하는 데 씁니다.
- 기본 모드에는 온도가 없으므로 열화상 카메라와 열 노출은 없습니다(Pro, 잠김).
- Go2 로봇과 ROS 2를 묶은 소방 로봇 학습 환경 전체는 이 배포에 들어 있지 않습니다. 필요하면 문의 바랍니다.

### 6.5 불꽃 세부 (FX), 0.91.0부터

**0.91.0부터 들어 있습니다.** 6.3절의 기본 불꽃은 열방출률을 0.1 m 격자로 옮긴 것이라 매끈한 덩어리로 보입니다. 불꽃 세부(FX)는
불 둘레의 작은 상자에서 불꽃을 고운 격자(기본 약 1.7 cm)로 따로 풀어, Mantaflow 불꽃처럼 깜빡이고 작게 흔들리는 불꽃을 만듭니다.
불이 어디서 얼마나 크게 타는지는 BUL:C 계산의 열방출률(`hrrpuv`)을 따릅니다. GPU에서 돌고, 결과 불꽃은 복사 없이 렌더러로
넘어갑니다.

**사용 방법 1: 예제로 영상 만들기**

```bat
python C:\BULBIT\examples\render_fx_video.py iso9705_200kw_nvdb 20 25 fx_20_25
python C:\BULBIT\examples\render_fx_video.py iso9705_200kw_nvdb 20 25 basic_20_25 --flame basic
```

20~25 s를 30 fps PNG(`frame_NNNN.png`)로 그리고, ffmpeg이 PATH에 있으면 `video.mp4`도 만듭니다. 첫 줄은 FX 불꽃, 둘째 줄은
비교용 기본 불꽃(0.90 방식)입니다. FX는 시작 시각 3 s 전부터 미리 돌려(예열) 불꽃 크기를 맞춘 뒤 그립니다.

| 옵션 | 뜻 |
|---|---|
| `--eye X Y Z`, `--target X Y Z`, `--hfov`, `--size W H` | 카메라(m, 계산 좌표). 주지 않으면 불꽃 중심 앞 4 m |
| `--no-smoke`, `--bg R G B`, `--lights N` | 연기 빼기, 배경색, 불꽃 점광원 수(0이면 없음) |
| `--box X0 Y0 Z0 X1 Y1 Z1` | FX 상자(m). 주지 않으면 그 구간의 코어 불꽃 둘레로 정합니다 |
| `--walls x- y- z- ...` | 닫힌 상자 면. 주지 않으면 상자가 바닥에 닿을 때 바닥(`z-`)만 닫습니다 |
| `--voxel` | FX 격자(m). 기본은 코어 칸의 1/6, 칸이 200만 개를 넘으면 키웁니다 |
| `--set 이름=값` | FX 값(아래 표) |
| `--pre` | 예열 시간(s, 기본 3) |

**사용 방법 2: 스크립트에서 쓰기**

```python
import bulbit
from bulbit.fx import FlameFX

r = bulbit.Renderer(mode="primary")
# ... 6.3절처럼 set_sigma(연기), set_look, set_ramps, 카메라를 준비합니다
fx = FlameFX(r, "iso9705_200kw_nvdb", t0=20.0, t1=25.0)   # 상자와 격자는 그 구간의 코어 불꽃을 보고 정합니다
print(fx.describe())                                      # 상자, 격자, 칸 수, 닫힌 면
fx.start()                                                # t0 - 3 s부터 t0까지 예열
while fx.t < fx.t1 - 1e-9:
    st = fx.step()                                        # 1/30 s 진행. 렌더러의 불꽃이 FX 불꽃으로 바뀝니다
    r.render([cam], W, H, depth=depth, download=False)
    r.composite(bg=bg, out=out)
fx.close()
```

- FX는 불꽃만 바꿉니다. 연기(`set_sigma`)는 프레임의 `smoke_sigma`를 6.3절처럼 따로 넣습니다.
- `fx.step()`은 `FxStats`를 돌려줍니다: 시각, 단계 수, 최대 속도, 수명, FX 불꽃 부피와 코어 불꽃 부피, 상자 안 열방출(kW) 등.
- `fx.download_flame()`은 불꽃 장(numpy)이고, `fx.lattice`는 그 격자입니다. 점광원은 이것으로 `lights_from_flame`을 부릅니다.
- 다른 불꽃을 `set_flame`으로 넣으면 그 불꽃이 쓰이고, 다음 `fx.step()`에서 다시 FX 불꽃으로 바뀝니다.
- Isaac Sim(6.4절)에서는 카메라 영상 1/30 s마다 `fx.step()`을 한 번 부르고 렌더하면 됩니다.

**어떻게 만드나**

- 코어 불꽃(`hrrpuv` > 200 kW/m³)의 바닥 칸에서 불꽃을 내보냅니다. 불꽃은 자기 열로 떠오르고, 수명 동안 줄어듭니다.
- 불꽃 세기에 비례한 소용돌이 강화(와도 가둠)와 프레임당 2~8 단계 계산이 깜빡임과 작은 소용돌이를 만듭니다.
- 크기: 수명을 매 프레임 조정해 FX 불꽃 부피가 코어 불꽃 부피를 따르게 합니다. 코어 불꽃(한 칸 넓힌) 밖으로 나간 불꽃은 지웁니다.
- 속도: 기본 모드에는 속도가 없으므로, 3.5·Q^(1/5) m/s(Q = 상자 안 열방출, kW)를 넘는 속도는 되돌립니다. 200 kW면 약 10 m/s입니다.

**자주 바꾸는 값** (`--set 이름=값` 또는 `FlameFX(..., 이름=값)`. 전체 목록은 `bulbit.fx.default_params()`)

| 이름 | 기본값 | 뜻 |
|---|---|---|
| `epsf` | 1.36 | 불꽃 안 소용돌이 세기. 낮추면 차분해집니다 |
| `eps0` | 0.15 | 불꽃 밖 소용돌이 세기 |
| `size_ratio` | 1.0 | FX 불꽃 부피 ÷ 코어 불꽃 부피의 목표. 키우면 불꽃이 커집니다 |
| `t_max` | 0.40 | 불꽃 온도(무차원). 높이면 빨리 오릅니다 |
| `u_cap` | 3.5 | 속도 상한 계수(0이면 끔) |
| `n_max` | 8 | 프레임당 최대 계산 단계 |

**벽에 붙은 불.** 기본 모드 프레임에는 벽 정보가 없습니다. 벽 옆 불은 상자를 벽에 맞추고 그 면을 닫으면 벽을 따라 섭니다.
예: 방 구석(벽 x = −0.1 m, y = −0.1 m, 천장 2.4 m)의 버너는 `--box -0.1 -0.1 0 0.9 0.9 2.4 --walls x- y- z- z+`.

**속도와 메모리.** RTX 5070 Ti에서 칸 25만~80만 개(1.7 cm 격자, 상자 1~2 m)에 프레임당 5~20 ms가 걸립니다(렌더 제외).
GPU 메모리는 칸 100만 개에 약 100 MB입니다.

**한계** (기본 모드라서)

- 프레임에 속도가 없어서, 바람이나 문 쪽 흐름에 기운 불꽃도 FX에서는 곧게 섭니다. 코어 불꽃 밖으로 나간 부분은 지워지므로
  기운 불꽃은 실제보다 낮고 넓어 보일 수 있습니다.
- 벽과 바닥 말고 다른 장애물(차 등)은 모릅니다. 불꽃이 그 안으로 들어갈 수 있으니 엔진의 깊이 버퍼로 가립니다(6.4절).
- 연기는 바꾸지 않습니다(코어의 `smoke_sigma` 그대로).

---

## 7. C / C++에서 쓰기

- 헤더 `include/bulbit.h`, 라이브러리 `bin/bulbit.dll`. ABI 버전은 `bb_abi_version()`(지금 4)으로 확인합니다.
- 흐름: `bb_renderer_new(mode, device, &r)` → `bb_set_sigma` / `bb_set_flame`(호스트 복사) 또는 `*_device`(장치 포인터 빌림)
  → `bb_set_look`(`bb_look_v0/v1/v2`로 채움), `bb_set_ramps`(`bb_ramps_v0`), `bb_set_lights` → `bb_render` → `bb_composite` 또는
  `bb_download_last` → `bb_renderer_free`.
- 오류: 함수는 0(성공), 1(오류), 2(잡힌 패닉)를 돌려줍니다. 1이나 2면 `bb_last_error()`가 이유를 돌려줍니다. 2가 나온 렌더러는
  다시 쓰지 말고 해제합니다.
- 격자 배열은 C 순서 [x][y][z](z가 가장 빠름), 원점은 셀 (0, 0, 0)의 낮은 모서리입니다.
- 불꽃 세부(ABI 4, 0.91.0부터): `bb_fx_params_default(&p)`로 채운 뒤 상자(`box_lo`, `box_hi`), 격자(`voxel`),
  닫힌 면(`walls`: 1 x−, 2 x+, 4 y−, 8 y+, 16 z−, 32 z+)을 정합니다.
  → `bb_fx_setup(r, &p, &코어 격자)` → 코어 프레임마다 `bb_fx_core_frame(r, t, hrrpuv, n)`(시간 순서, 호스트 배열)
  → `bb_fx_start(r, t0)` → 매 프레임 `bb_fx_step(r, &stats)` → `bb_render` → 다 쓰면 `bb_fx_clear(r)`.
  `bb_fx_start`와 `bb_fx_step`은 FX 불꽃을 렌더러의 불꽃으로 둡니다. 렌더러 하나에 FX 하나입니다.

---

## 8. 문제 해결

| 메시지 | 원인 | 할 일 |
|---|---|---|
| `LICENSE ERROR: 이 컴퓨터에서 BUL:BIT에 로그인하지 않았습니다` | 로그인하지 않음 | `bulbit_sim login` |
| `cannot listen on 127.0.0.1:9876` | 다른 로그인 창(BUL:C 포함)이 열려 있음 | 그 창을 닫고 다시 |
| `cannot reach the license server` | 인터넷·방화벽·프록시 | 연결을 확인하고 다시. Windows 프록시 설정을 따릅니다 |
| `이 BUL:C 라이선스를 다른 곳에서 쓰고 있습니다` | 세션 수 한도 | `bulbit_sim login --replace` |
| `the BUL:C license of this account does not include the core-simulation entitlement` | 계정의 라이선스에 계산 권한이 없음 | 문의 |
| `무료 이용 기간(15일 …)이 끝났습니다` (종료 코드 4) | 15일이 지남 | 문의 |
| `시스템 시계가 마지막 BUL:BIT 실행보다 이릅니다` | PC 시계가 뒤로 감 | 시계를 맞추고 다시 |
| `cuFFT 로드 실패` | `cufft64_12.dll`이 없음 | `bulbit_sim.exe`와 같은 폴더에 둡니다 |
| `CUDA error 222`, `PTX` | 드라이버가 오래됨 | NVIDIA 드라이버를 새로 설치 |
| `VRAM` | GPU 메모리 부족 | 격자를 줄이거나 셀을 키웁니다 |
| `bulbit.dll not found` | `BULBIT_DLL`이 틀림 | 6.1절대로 맞춤 |
| `BUL:BIT Pro is locked` | Pro 기능을 요청함 | 기본 모드 기능만 씁니다 |
| `the flame detail (FX) needs bulbit.dll ABI 4` | 0.90.0 등 FX가 없는 `bulbit.dll`을 씀 | `BULBIT_DLL`을 0.91.0의 `bin\bulbit.dll`로 |
| `the frames carry no hrrpuv grid` | `hrrpuv`가 없는 옛 프레임 | 0.90.0 이후 `bulbit_sim`으로 다시 계산 |
| `no core flame (hrrpuv > 200 kW/m3)` | 그 구간에 불꽃이 없음 | 시작·끝 시각을 바꾸거나 `--box`를 줌 |
| FX 불꽃이 너무 크거나 작음 | 크기 목표 | `--set size_ratio=0.7`(작게) 또는 `1.5`(크게) |

---

## 9. 문의

- BUL:BIT 구매·이용 문의: **simul@msimul.com**, **https://bulc.msimul.com**
- BUL:C 계정 만들기: https://bulc.msimul.com
