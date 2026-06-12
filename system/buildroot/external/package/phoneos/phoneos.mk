################################################################################
#
# phoneos
#
################################################################################

PHONEOS_SITE = $(BR2_EXTERNAL_PHONEOS_PATH)/../../..
PHONEOS_SITE_METHOD = local
PHONEOS_LICENSE = MIT
PHONEOS_DEPENDENCIES = lvgl lv_drivers

PHONEOS_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

define PHONEOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/build/ui/launcher/phoneos-launcher $(TARGET_DIR)/usr/bin/phoneos-launcher
endef

$(eval $(cmake-package))
