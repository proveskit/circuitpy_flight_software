#ifndef _FUNCTIONS_H
#define _FUNCTIONS_H
#include <stdio.h>
#include <neopixel/neopixel.h>
#include <tools/tools.h>
#include <pysquared/pysquared.h>
#include <device_drivers/TCA9548A.h>
#include <Big_Data/Big_Data.h>
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"

class satellite_functions{
    public:
    satellite_functions(pysquared& satellite);
    void battery_manager();
    void battery_heater();
    void all_face_data();
    private:
    tools t;
    pysquared& c;
    Big_Data b;
};
#endif
