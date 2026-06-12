add_library(phoneos_notification STATIC
    notification_service.c
)

target_include_directories(phoneos_notification
    PUBLIC
        ${PROJECT_SOURCE_DIR}/system/framework/include
)