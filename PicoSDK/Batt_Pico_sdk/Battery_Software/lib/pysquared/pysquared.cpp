#include "pysquared.h"
                                                      //instantiate tools class in pysquared
pysquared::pysquared(neopixel neo) : 
battery_power(i2c0, 0x40), solar_power(i2c0, 0x44), internal_temp(i2c0, 0x4f), led_driver(i2c0, 0x56), i2c_mux(i2c0,0x77),
adc(i2c0,0x48),
t(true, "[PYSQUARED] "){
    /*
        Pin Definitions
    */
    relay_pin = 15;
    vbus_reset_pin = 14;
    i2c_reset_pin = 7;
    rf_enable_pin = 12;
    d0_pin = 29;
    i2c_sda1_pin = 2;
    i2c_scl1_pin = 3;
    i2c_sda0_pin = 4;
    i2c_scl0_pin = 5;
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
        gpio_init(d0_pin);
        gpio_set_dir(d0_pin, GPIO_IN);

        gpio_put(i2c_reset_pin, true); 
        t.debug_print("GPIO Pins Initialized!\n");
        /*
            PWM init
        */

        t.debug_print("PWM Pins Initialized!\n");
        /*
            I2C init
        */
        i2c_init(i2c0, 400*1000);
        gpio_set_function(i2c_sda0_pin, GPIO_FUNC_I2C);
        gpio_set_function(i2c_scl0_pin, GPIO_FUNC_I2C);
        t.i2c_scan(i2c0);
        i2c_init(i2c1, 400*1000);
        gpio_set_function(i2c_sda1_pin, GPIO_FUNC_I2C);
        gpio_set_function(i2c_scl1_pin, GPIO_FUNC_I2C);
        t.i2c_scan(i2c1);
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
        try{
            led_driver.configure();
            all_faces_on();
            t.debug_print("LED Driver Initialized!\n");
        }
        catch(...){
            t.debug_print("ERROR initializing LED Driver!\n");
            error_count++;
        }
        /*
            I2C Multiplexer init
        */
        try{ 
            i2c_mux.configure();
            i2c_mux.scanChannels();
            t.debug_print("I2C Multiplexer Initialized!\n");
        }
        catch(...){
            t.debug_print("ERROR initializing I2C Multiplexer!\n");
            error_count++;
        }
        /*
            Thermocouple
        */
        try{ 
            adc.configure();
            t.debug_print("Thermocouple ADC Initialized!\n");
        }
        catch(...){
            t.debug_print("ERROR initializing Thermocouple ADC!\n");
            error_count++;
        }
        /*
            Battery Power Monitor init
        */
        try{
            battery_power.configure();
            t.debug_print("Battery Power Monitor Initialized!\n");
        }
        catch(...){
            t.debug_print("ERROR initializing Battery Power Monitor!\n");
            error_count++;
        }
        /*
            Solar Power Monitor init
        */
       try{
            solar_power.configure();
            t.debug_print("Solar Power Monitor Initialized!\n");
        }
        catch(...){
            t.debug_print("ERROR initializing Solar Power Monitor!\n");
            error_count++;
        }
        t.debug_print("Hardware fully initialized!\n");
    }
    catch(...){
        t.debug_print("ERROR Initializing Hardware: \n");
        error_count++;
    }
}

void pysquared::check_reboot(){
    try{
        t.debug_print("Checking for reboot\n");
    }
    catch(...){
        t.debug_print("ERROR while checking for reboot!\n");
        error_count++;
    }
    return;
}

void pysquared::all_faces_on(){
    try{
        t.debug_print("Attempting to turn all faces on!\n");
        led_driver.setPortState(0,true);
        led_driver.setPortState(1,true);
        led_driver.setPortState(2,true);
        led_driver.setPortState(3,true);
        led_driver.setPortState(4,true);
        t.debug_print("all faces turned on!\n");
    }
    catch(...){
        t.debug_print("ERROR while turning all faces on!\n");
        error_count++;
    }
}

void pysquared::all_faces_off(){
    try{
        t.debug_print("Attempting to turn all faces off!\n");
        led_driver.setPortState(0,false);
        led_driver.setPortState(1,false);
        led_driver.setPortState(2,false);
        led_driver.setPortState(3,false);
        led_driver.setPortState(4,false);
        t.debug_print("all faces turned off!\n");
    }
    catch(...){
        t.debug_print("ERROR while turning all faces off!\n");
        error_count++;
    }
}

void pysquared::heater_on(){
    try{
        t.debug_print("Turning Heater on...\n");
        led_driver.setDutyCycle(15,2048);
        t.debug_print("done!\n");
    }
    catch(...){
        t.debug_print("ERROR while turning on the heater!\n");
        led_driver.setDutyCycle(15,0);
        error_count++;
    }
}

void pysquared::heater_off(){
    try{
        t.debug_print("Turning Heater off...\n");
        led_driver.setDutyCycle(15,0);
        t.debug_print("done!\n");
    }
/*     catch(const std::exception &e){
        printf(e.what());
        error_count++;
    } */
    catch(...){
        t.debug_print("ERROR while turning off the heater!\n");
        error_count++;
    }
}

uint8_t pysquared::get_power_mode() {return pwr_mode;}
float pysquared::get_thermocouple_temp(){
    try{
        float val=static_cast< float >(adc.readSingleEnded(1))*2.048/2048;
        printf("ADC Voltage measured: %.3f\n", val);
        return ((val-1.25)/0.004);
    }
    catch(...){
        t.debug_print("ERROR while getting thermocouple temperature!\n");
        error_count++;
        return 0;
    }
}
float pysquared::get_internal_temp() {
    try{
        float temp;
        for(int i = 0; i<50; i++){
            temp+=internal_temp.readTemperature();
        }
        return temp/50;
    }
    catch(...){
        t.debug_print("ERROR while getting internal temperature!\n");
        error_count++;
        return 0;
    }
}
float pysquared::get_battery_voltage(){
    try{
        float temp;
        for(int i = 0; i<50; i++){
            temp+=battery_power.readBusVoltage();
        }
        return temp/50;
    }
    catch(...){
        t.debug_print("ERROR while getting battery voltage!\n");
        error_count++;
        return 0;
    }
}
float pysquared::get_draw_current(){
    try{
        float temp;
        for(int i = 0; i<50; i++){
            temp+=battery_power.readCurrent();
        }
        return temp/50;
    }
    catch(...){
        t.debug_print("ERROR while getting draw current!\n");
        error_count++;
        return 0;
    }
}
float pysquared::get_charge_voltage(){
    try{
        float temp;
        for(int i = 0; i<50; i++){
            temp+=solar_power.readBusVoltage();
        }
        return temp/50;
    }
    catch(...){
        t.debug_print("ERROR while getting charge voltage!\n");
        error_count++;
        return 0;
    }
}
float pysquared::get_charge_current(){
    try{
        float temp;
        for(int i = 0; i<50; i++){
            temp+=solar_power.readCurrent();
        }
    return temp/50;
    }
    catch(...){
        t.debug_print("ERROR while getting charge current!\n");
        error_count++;
        return 0;
    }
}
