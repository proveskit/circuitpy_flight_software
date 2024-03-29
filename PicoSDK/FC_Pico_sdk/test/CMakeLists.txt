project(my_project)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# rest of your project
if (TARGET tinyusb_device)
    add_executable(my_project
            helloworld.c
            )

    # pull in common dependencies
    target_link_libraries(my_project pico_stdlib)

    # enable usb output, disable uart output
    pico_enable_stdio_usb(my_project 1)
    pico_enable_stdio_uart(my_project 0)

    # create map/bin/hex/uf2 file etc.
    pico_add_extra_outputs(my_project)
elseif(PICO_ON_DEVICE)
    message(WARNING "not building hello_usb because TinyUSB submodule is not initialized in the SDK")
endif()