# PhoneOS Phase 1 (Raspberry Pi Zero 2 W)

Linux-based lightweight smartphone shell using Buildroot + LVGL.

## Implemented in Phase 1

- Buildroot external tree and Pi Zero 2 W defconfig
- Full-screen LVGL launcher runtime
- Status bar with clock + notification feed
- Home screen app grid
- Application framework + app registry
- Built-in apps: Phone, SMS, Camera, Gallery, Settings
- Notification service
- App management bootstrap

## Directory layout

```
/kernel
/system
/services
/apps
/ui
/drivers
/assets
```

## Host prerequisites

- Linux host with Buildroot dependencies (`gcc`, `make`, `git`, `bison`, `flex`, `python3`, `rsync`, etc.)
- Buildroot source tree (recommended 2024.02+)

## WSL prerequisites

- WSL2 with WSLg enabled or another GUI path available
- `cmake`, `build-essential`, `git`, `pkg-config`, and `libsdl2-dev`
- Outbound network access on first configure so CMake can fetch LVGL for the WSL backend

## Build steps

1. Clone Buildroot:

```bash
git clone https://github.com/buildroot/buildroot.git ~/buildroot
cd ~/buildroot
git checkout 2024.02.9
```

2. From the PhoneOS project root, run:

```bash
chmod +x system/buildroot/build.sh
system/buildroot/build.sh ~/buildroot
```

If you do not pass a Buildroot path, the project bootstraps Buildroot into `third_party/buildroot` automatically on the first build.

3. Output artifacts:

- `out/buildroot-zero2w/images/sdcard.img`
- `out/buildroot-zero2w/images/rootfs.ext4`
- `out/buildroot-zero2w/images/zImage`

## Flash and run

1. Write `sdcard.img` to microSD.
2. Boot Raspberry Pi Zero 2 W.
3. System starts `phoneos-launcher` from `/etc/init.d/S99phoneos` on `tty1`.
4. Touchscreen events are read from `/dev/input/event0` via LVGL evdev backend.

## Run in WSL

1. Install dependencies inside WSL:

```bash
sudo apt update
sudo apt install -y build-essential cmake git pkg-config libsdl2-dev
```

2. Build the native WSL launcher:

```bash
chmod +x system/wsl/build.sh
system/wsl/build.sh
```

3. Run the SDL launcher window:

```bash
chmod +x system/wsl/run.sh
system/wsl/run.sh
```

The WSL path uses the same launcher, home screen, status bar, and built-in apps, but renders through SDL2 instead of the Pi framebuffer.

## Runtime targets

- RAM target device: 512 MB
- Idle RAM budget (target): under 150 MB
- Display path: Linux framebuffer (`/dev/fb0`)
- Input path: Linux evdev (`/dev/input/event*`)

## Notes

- Current UI is intentionally lightweight: no compositor, no browser engine, no X11/Wayland.
- App implementations are functional shell modules in this phase and designed for incremental backend integration.