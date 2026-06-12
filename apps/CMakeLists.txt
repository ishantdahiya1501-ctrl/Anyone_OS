add_library(phoneos_apps STATIC
    init.c
    phone/phone_app.c
    sms/sms_app.c
    camera/camera_app.c
    gallery/gallery_app.c
    settings/settings_app.c
)

target_include_directories(phoneos_apps
    PUBLIC
        ${PROJECT_SOURCE_DIR}/system/framework/include
)

target_link_libraries(phoneos_apps
    PUBLIC
        phoneos_framework
)