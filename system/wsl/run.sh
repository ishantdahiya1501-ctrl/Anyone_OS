#!/usr/bin/env sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
BUILD_DIR="$PROJECT_DIR/out/wsl"
BINARY="$BUILD_DIR/ui/launcher/phoneos-launcher"

if [ ! -x "$BINARY" ]; then
    "$PROJECT_DIR/system/wsl/build.sh"
fi

exec "$BINARY"
