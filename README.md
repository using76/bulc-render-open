# BUL:BIT (불빛) — 화재 렌더러

> BUL:C computes the fire. BUL:BIT renders it. — 불씨(BUL:C)가 불을 계산하고, 불빛(BUL:BIT)이 그 불을 그린다.

**BUL:BIT(불빛)는 화재 렌더러입니다.** 메테오시뮬레이션의 화재 시뮬레이터 BUL:C(불씨) GPU 코어로 계산한 불꽃과 연기를 영상,
게임 엔진, 로봇 시뮬레이터(NVIDIA Isaac Sim)의 카메라 화면으로 그립니다.

이 저장소에는 **빌드된 프로그램만** 있습니다(소스 코드는 공개하지 않습니다). 프로그램은 [Releases](https://github.com/using76/bulc-render-open/releases)에서 받습니다.

- **[사용설명서](docs/MANUAL.md)**: 설치, 로그인, 계산, 렌더, Isaac Sim, 문제 해결
- **[이용 조건](LICENSE.md)**: 15일 무료 이용권, 연구·교육용, 상업적 사용 불가

---

## 샘플

### BUL:BIT 기본 모드 렌더

![BUL:BIT 기본 모드 렌더: 자동차운반선 갑판 EV 화재](docs/samples/bulbit_basic_ev_deck.jpg)

자동차운반선 갑판의 전기차 화재(열방출률 1.876·t², 10 MW까지)를 `bulbit_sim`으로 계산하고, 그 기본 모드 프레임을
BUL:BIT 렌더러로 그렸습니다. 불꽃은 열방출률(`hrrpuv`)로, 연기는 그을음(`smoke_sigma`)으로 그립니다. 카메라 두 대, 20·40·70·100 s.
차와 갑판 같은 형상은 그리지 않았습니다(형상은 쓰는 엔진이 그립니다). 차 모양으로 비어 보이는 곳은 연기가 들어가지 않는
차 안쪽입니다.

### 홍보 영상에서

| ISO 9705 방 구석 화재 | 사족보행 로봇이 불타는 차 옆을 걸어가 포탑을 겨눔 |
|---|---|
| ![ISO 9705 방 구석 화재](docs/samples/watermist_iso9705_corner_fire.webp) | ![사족보행 로봇과 차량 화재](docs/samples/robot_quadruped_walk_turret_aim.webp) |
| [MP4 (10 s, 1280×720)](docs/samples/watermist_iso9705_corner_fire.mp4) | [MP4 (10 s, 1280×720)](docs/samples/robot_quadruped_walk_turret_aim.mp4) |
| 미분무 소화 홍보 영상의 도입부입니다. **BUL:C 계산이 아니라 Blender로 그린 개요 장면입니다**(불꽃은 BULC기반 형상작성후 Blender Mantaflow, 렌더는 EEVEE, 연기는 BULC기반). | 불과 연기는 **BUL:C 계산**입니다(자동차운반선 갑판 EV 화재, 28~32 s, 약 1.5~1.9 MW). 렌더는 지금의 BUL:BIT 렌더러보다 먼저 쓰던 Blender Cycles 파이프라인입니다. **로봇과 그 움직임은 일러스트**(스크립트 애니메이션)이고, 학습한 정책이나 Isaac Sim 물리가 아닙니다 |

### 개발 중: 불빛 BUL:BIT 불꽃 세부(FX)

![Mantaflow 원본, BUL:C(기존 CFD), 불빛 BUL:BIT 불꽃 비교](docs/samples/bulbit_fx_flame_detail_preview.webp)

[MP4 (6 s, 792×720)](docs/samples/bulbit_fx_flame_detail_preview.mp4)

다음 버전에 넣을 불꽃 세부 기능(FX)의 첫 비교입니다. **0.90.0 배포판에는 아직 들어 있지 않습니다.**
ISO 9705 방 구석 화재(약 200 kW)를 BUL:C로 계산하고, 구석의 1 × 1 × 2.4 m 상자만 1.67 cm 격자로 다시 풀었습니다.
세 화면 모두 불꽃에서 같은 거리에 둔 카메라로 불꽃만 그렸습니다.

- **Mantaflow 원본**: 위 미분무 영상에 쓴 Blender Mantaflow 불꽃(1.5 cm 격자)
- **BUL:C (기존 CFD)**: BUL:C 계산을 따라가는 불꽃, FX 없음. 매끈한 기둥입니다
- **불빛 BUL:BIT**: 같은 계산에 FX를 켰습니다. 불꽃 크기는 BUL:C 계산에 맞추고(10 cm 칸으로 묶은 불꽃 부피가
  BUL:C의 1.01배), 작은 소용돌이와 깜빡임을 더합니다

| | Mantaflow 원본 | BUL:C (기존 CFD) | 불빛 BUL:BIT |
|---|---|---|---|
| 불꽃 꼭대기 | 1.1 m | 2.4 m (천장) | 2.4 m (천장) |
| 밝기 깜빡임 | 0.155 | 0.025 | 0.253 |
| 윤곽 이동 (픽셀/프레임) | 2.7 | 0.3 | 4.1 |

Mantaflow 불꽃은 영상용으로 따로 맞춘 크기입니다. BUL:C 계산에서는 이 구석 화재의 불꽃이 천장까지 닿고, BUL:BIT는 그
크기를 따릅니다. 아직 보정 중입니다. 지금은 깜빡임이 Mantaflow보다 세고, 버너 바로 위 아래쪽은 아직 매끈합니다.

---

## 들어 있는 것

| 구성 | 파일 | 하는 일 |
|---|---|---|
| 계산 코어 | `bin/bulbit_sim.exe` | FDS 형식 화재 입력(`.fds`)을 GPU로 계산하고, 렌더용 NanoVDB 프레임만 씁니다 |
| 렌더 라이브러리 | `bin/bulbit.dll`, `include/bulbit.h` | 연기와 불꽃 볼륨을 카메라 영상으로 그립니다(CUDA, C ABI) |
| Python | `python/bulbit`, `python/bulbit_basic` | 렌더러 바인딩(torch·Warp·CuPy CUDA 배열을 복사 없이), 프레임 읽기, 열방출률로 불꽃 만들기 |
| 예제 | `examples/` | ISO 9705 방 200 kW 화재 입력, 프레임 한 장을 PNG로 그리는 스크립트 |

**기본 모드만 열려 있습니다.** 프레임마다 `smoke_sigma`(그을음 소광계수, 1/m), `hrrpuv`(열방출률, kW/m³),
`visibility`(시야, m)를 내보내고, 불꽃과 연기를 그립니다. Pro 기능(온도, 속도, CO, CO₂, 압력, 열화상 등)은 잠겨 있습니다.

BUL:BIT는 영상과 로봇·AI 학습용입니다. 공학 출력(측정점, CSV, 슬라이스)은 내지 않습니다. 공학 해석에는 BUL:C를 쓰십시오.

## 필요한 것

- Windows 10/11 64비트
- NVIDIA GPU, 연산 능력 8.6 이상(GeForce RTX 30·40·50 계열 등)과 CUDA 13.1 이상을 지원하는 드라이버
- BUL:C 계정(https://bulc.msimul.com). 로그인할 때 인터넷이 필요합니다
- 렌더에는 Python 3.10+와 numpy, scipy, torch(CUDA). Isaac Sim·Isaac Lab의 Python에 모두 들어 있습니다

## 빠른 시작

```bat
:: 1. Releases의 bulbit-0.90.0-win64.zip을 C:\BULBIT 에 풉니다

:: 2. 로그인: 이용 조건이 나오고, 브라우저에서 BUL:C 계정으로 로그인합니다
C:\BULBIT\bin\bulbit_sim.exe login

:: 3. 계산: iso9705_200kw_nvdb\ 에 0.1 s마다 프레임이 생깁니다
copy C:\BULBIT\examples\iso9705_200kw.fds .
C:\BULBIT\bin\bulbit_sim.exe iso9705_200kw.fds > run.log 2>&1

:: 4. 렌더: 20 s 프레임의 불꽃과 연기를 PNG로
set BULBIT_HOME=C:\BULBIT
python C:\BULBIT\examples\render_basic_frame.py iso9705_200kw_nvdb 20.0 fire_20s.png
```

자세한 내용은 [사용설명서](docs/MANUAL.md)에 있습니다.

## 이용 조건

- BUL:C 계정으로 로그인한 PC에서 **처음 로그인한 때부터 15일** 동안 쓸 수 있습니다.
- 무료체험 버전은 **연구와 교육 목적으로만** 쓸 수 있습니다. **상업적 용도로는 쓸 수 없습니다.**
- 15일이 지난 뒤에도 쓰려면 문의 바랍니다: **simul@msimul.com**, **https://bulc.msimul.com**
- 상업용 이용은 문의 바랍니다.
- 전체 조건: [LICENSE.md](LICENSE.md). 함께 배포하는 NVIDIA cuFFT: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

## English

**BUL:BIT is a fire renderer.** It draws the flames and smoke computed by the GPU core of BUL:C, Meteor Simulation's fire
simulator, into video, game engines and robot simulators (NVIDIA Isaac Sim). This repository holds the built program only;
download it from [Releases](https://github.com/using76/bulc-render-open/releases).

- `bulbit_sim.exe` computes a fire from an FDS-format input and writes NanoVDB frames for rendering (no engineering outputs).
- `bulbit.dll` (C ABI) and the `bulbit` Python package render the smoke and flame volumes; `bulbit_basic` reads the frames
  and makes the flame field from the heat release rate.
- **Basic mode only:** each frame carries `smoke_sigma` (soot extinction, 1/m), `hrrpuv` (heat release rate, kW/m³) and
  `visibility` (m); fire and smoke are rendered. Pro features (temperature, velocity, CO, CO₂, pressure, thermal) are locked.
- **License:** sign in with a BUL:C account (`bulbit_sim login`); usable for **15 days** from the first sign-in on a computer,
  **research and education only, no commercial use**. To continue, contact simul@msimul.com or https://bulc.msimul.com.
- Requirements: Windows 10/11 x64, an NVIDIA GPU with compute capability 8.6 or higher and a driver for CUDA 13.1 or later.
- The promo-film clips above are honest about what they are: the ISO 9705 clip is a Blender illustration (not BUL:C); in
  the robot clip the fire and smoke are BUL:C results rendered with an earlier Blender pipeline, and the robot is an
  illustration.
- **In development (not in 0.90.0): BUL:BIT flame detail (FX).** A first comparison on the ISO 9705 corner fire:
  Blender Mantaflow (the promo film's flame), BUL:C (existing CFD, no FX) and BUL:BIT with FX, which keeps the flame size
  of the BUL:C result and adds small eddies and flicker ([MP4](docs/samples/bulbit_fx_flame_detail_preview.mp4)).
  Still being calibrated.

© 2026 메테오시뮬레이션 (Meteor Simulation). All rights reserved.
