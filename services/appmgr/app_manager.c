#include "phoneos/app_manager.h"
#include "phoneos/app_registry.h"

void phoneos_register_builtin_apps(void);

void phoneos_app_manager_init(void)
{
    phoneos_clear_apps();
    phoneos_register_builtin_apps();
}