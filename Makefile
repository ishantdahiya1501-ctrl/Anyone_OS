PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BUILDROOT_DIR ?= $(PROJECT_ROOT)/third_party/buildroot
WSL_BUILD_DIR := $(PROJECT_ROOT)/out/wsl
BR_BUILD_DIR := $(PROJECT_ROOT)/out/buildroot-zero2w
WSL_BINARY := $(WSL_BUILD_DIR)/ui/launcher/phoneos-launcher

.PHONY: help wsl buildroot run clean

help:
	@echo "PhoneOS build targets:"
	@echo "  make wsl BUILDROOT_DIR=/path/to/buildroot  Build the native SDL2 WSL launcher"
	@echo "  make buildroot BUILDROOT_DIR=/path/to/buildroot  Build the Raspberry Pi Zero 2 W image"
	@echo "  make run   Run the WSL launcher after building it"
	@echo "  make clean Remove local build output under out/"

wsl:
	@chmod +x "$(PROJECT_ROOT)/system/wsl/build.sh"
	@"$(PROJECT_ROOT)/system/wsl/build.sh"

buildroot:
	@chmod +x "$(PROJECT_ROOT)/system/buildroot/build.sh"
	@"$(PROJECT_ROOT)/system/buildroot/build.sh" "$(BUILDROOT_DIR)"

run: wsl
	@"$(WSL_BINARY)"

clean:
	@rm -rf "$(PROJECT_ROOT)/out/wsl" "$(PROJECT_ROOT)/out/buildroot-zero2w"