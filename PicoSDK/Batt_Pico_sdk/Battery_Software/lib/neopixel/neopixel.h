#ifndef _NEOPIXEL_H
#define _NEOPIXEL_H
#include "hardware/pio.h"
#include <stdio.h>
#include "pico/stdlib.h"
class neopixel{
public:
    PIO pio_neo;
    uint sm_neo;
    neopixel(PIO pio, uint sm);
    void put_pixel(int pixel_grb);
    uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b);
};
#endif