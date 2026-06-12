add_subdirectory(notification)
add_subdirectory(appmgr)

add_library(phoneos_services INTERFACE)
target_link_libraries(phoneos_services
    INTERFACE
        phoneos_notification
        phoneos_appmgr
)