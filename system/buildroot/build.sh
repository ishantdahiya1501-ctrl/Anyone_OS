#!/usr/bin/env sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
OUT_DIR="$PROJECT_DIR/out/buildroot-zero2w"
BUILDROOT_DIR="${BUILDROOT_DIR:-${1:-$PROJECT_DIR/third_party/buildroot}}"
DEFCONFIG="raspberrypizero2w_defconfig"

if [ ! -f "$BUILDROOT_DIR/Makefile" ]; then
    echo "Buildroot root not found: $BUILDROOT_DIR"
    exit 1
fi

if [ ! -f "$BUILDROOT_DIR/configs/$DEFCONFIG" ]; then
    echo "Missing defconfig: $DEFCONFIG"
    exit 1
fi

mkdir -p "$OUT_DIR"

# Step 1: configure
make -C "$BUILDROOT_DIR" O="$OUT_DIR" "$DEFCONFIG"

# Step 2: build
make -C "$BUILDROOT_DIR" O="$OUT_DIR"

echo "Build complete: $OUT_DIR/images"