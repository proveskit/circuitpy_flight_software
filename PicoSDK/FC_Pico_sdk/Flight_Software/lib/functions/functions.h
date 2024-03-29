#ifndef _FUNCTIONS_H
#define _FUNCTIONS_H
#include <stdio.h>
#include <neopixel/neopixel.h>
#include <tools/tools.h>
#include <pysquared/pysquared.h>
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"

class satellite_functions{
    public:
    satellite_functions(pysquared satellite);
};
#endif