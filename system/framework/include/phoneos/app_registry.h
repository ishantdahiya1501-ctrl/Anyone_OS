#ifndef PHONEOS_APP_REGISTRY_H
#define PHONEOS_APP_REGISTRY_H

#include <stddef.h>

#include "phoneos/app.h"

#define PHONEOS_MAX_APPS 24

int phoneos_register_app(const phoneos_app_t *app);
size_t phoneos_app_count(void);
const phoneos_app_t *phoneos_get_app(size_t index);
void phoneos_clear_apps(void);

#endif