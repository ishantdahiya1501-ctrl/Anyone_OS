#ifndef PHONEOS_LAUNCHER_H
#define PHONEOS_LAUNCHER_H

#include "phoneos/app.h"

void phoneos_launcher_init(lv_obj_t *root);
void phoneos_launcher_open_app(const phoneos_app_t *app);
void phoneos_launcher_show_home(void);

#endif