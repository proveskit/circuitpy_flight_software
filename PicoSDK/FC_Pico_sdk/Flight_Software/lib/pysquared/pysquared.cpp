#include "pysquared.h"
                                                      //instantiate tools class in pysquared
pysquared::pysquared(neopixel neo) : accel(i2c1, 0x19), mag(i2c1, 0x1E), t(true, "[PYSQUARED] "){
    /*
        Pin Definitions
    */
    relay_pin = 15;
    vbus_reset_pin = 14;
    i2c_reset_pin = 7;
    rf_enable_pin = 12;
    rf_reset_pin = 20;
    rf_dio0_pin = 23;
    rf_dio4_pin = 22;
    d0_pin = 29;
    i2c_sda1_pin = 2;
    i2c_scl1_pin = 3;
    /*
        Initialize hardware core to operations on satellite.
    */
    try {
        t.debug_print("Figure out how to write to flash memory\n");                 //figure our how to section out some memory for flags
        pwr_mode=2;
        /*
            GPIO init
        */
        gpio_init(relay_pin);
        gpio_set_dir(relay_pin, GPIO_OUT);
        gpio_init(vbus_reset_pin);
        gpio_set_dir(vbus_reset_pin, GPIO_OUT);
        gpio_init(i2c_reset_pin);
        gpio_set_dir(i2c_reset_pin, GPIO_OUT);
        gpio_init(rf_enable_pin);
        gpio_set_dir(rf_enable_pin, GPIO_OUT);
        gpio_init(rf_reset_pin);
        gpio_set_dir(rf_reset_pin, GPIO_OUT);
        gpio_init(rf_dio0_pin);
        gpio_set_dir(rf_dio0_pin, GPIO_IN);
        gpio_init(rf_dio4_pin);
        gpio_set_dir(rf_dio4_pin, GPIO_IN);
        gpio_init(d0_pin);
        gpio_set_dir(d0_pin, GPIO_IN);
        t.debug_print("GPIO Pins Initialized!\n");
        /*
            PWM init
        */

        t.debug_print("PWM Pins Initialized!\n");
        /*
            I2C init
        */

        t.debug_print("I2C Bus Initialized!\n");
        /*
            SPI init
        */

        t.debug_print("SPI Bus Initialized!\n");
        /*
            UART init
        */

        t.debug_print("UART Bus Initialized!\n");
        /*
            LED Driver init
        */

        t.debug_print("LED Driver Initialized!\n");
        /*
            I2C Multiplexer init
        */

        t.debug_print("I2C Multiplexer Initialized!\n");
        /*
            Temperature sensor init
        */
        i2c_init(i2c1, 400*1000);
        gpio_set_function(i2c_sda1_pin, GPIO_FUNC_I2C);
        gpio_set_function(i2c_scl1_pin, GPIO_FUNC_I2C);
        t.i2c_scan(i2c1);
        t.debug_print("Temperature Sensor Initialized!\n");
        /*
            Battery Power Monitor init
        */

        t.debug_print("Battery Power Monitor Initialized!\n");
        /*
            Solar Power Monitor init
        */

        t.debug_print("Solar Power Monitor Initialized!\n");
        /*
            Magnetometer init
        */
        try{
            mag.init();
            t.debug_print("Magnetometer Initialized!\n");
        }
        catch(const char* e){
            t.debug_print("Error Initializing Magnetometer: \n");
        }
        /*
            Accelerometer init
        */
        try{
            accel.init();
            t.debug_print("Accelerometer Initialized!\n");
        }
        catch(const char* e){
            t.debug_print("Error Initializing Accelerometer: \n");
        }
        /*
            Gyroscope init
        */

        t.debug_print("Gyroscope Initialized!\n");
        t.debug_print("Hardware fully initialized!\n");
    }
    catch(const char* e){
        t.debug_print("Error Initializing Hardware: \n");
    }
}

void pysquared::check_reboot(){
    t.debug_print("Checking for reboot\n");
    return;
}
