#ifndef PHONEOS_HOME_SCREEN_H
#define PHONEOS_HOME_SCREEN_H

#include <lvgl.h>

void phoneos_home_screen_create(lv_obj_t *parent, void (*on_app_selected)(const char *app_id));

#endif