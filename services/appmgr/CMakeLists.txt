add_library(phoneos_appmgr STATIC
    app_manager.c
)

target_include_directories(phoneos_appmgr
    PUBLIC
        ${PROJECT_SOURCE_DIR}/system/framework/include
)

target_link_libraries(phoneos_appmgr
    PUBLIC
        phoneos_apps
        phoneos_framework
)