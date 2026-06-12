#!/usr/bin/env sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
BUILD_DIR="$PROJECT_DIR/out/wsl"

for tool in cmake git cc pkg-config; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Missing required tool: $tool"
        echo "Install the WSL dependencies with:"
        echo "  sudo apt update && sudo apt install -y build-essential cmake git pkg-config libsdl2-dev"
        exit 1
    fi
done

if ! pkg-config --exists sdl2; then
    echo "Missing SDL2 development files."
    echo "Install them with:"
    echo "  sudo apt update && sudo apt install -y libsdl2-dev"
    exit 1
fi

mkdir -p "$BUILD_DIR"

cmake -S "$PROJECT_DIR" -B "$BUILD_DIR" -DPHONEOS_WSL=ON
cmake --build "$BUILD_DIR" -j"$(getconf _NPROCESSORS_ONLN)"

echo "Build complete: $BUILD_DIR/ui/launcher/phoneos-launcher"
