#include "phoneos/app_registry.h"

const phoneos_app_t *phone_app_descriptor(void);
const phoneos_app_t *sms_app_descriptor(void);
const phoneos_app_t *camera_app_descriptor(void);
const phoneos_app_t *gallery_app_descriptor(void);
const phoneos_app_t *settings_app_descriptor(void);

void phoneos_register_builtin_apps(void)
{
    (void)phoneos_register_app(phone_app_descriptor());
    (void)phoneos_register_app(sms_app_descriptor());
    (void)phoneos_register_app(camera_app_descriptor());
    (void)phoneos_register_app(gallery_app_descriptor());
    (void)phoneos_register_app(settings_app_descriptor());
}