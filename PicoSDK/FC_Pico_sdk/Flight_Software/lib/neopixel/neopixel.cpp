#include "neopixel.h"
neopixel::neopixel(PIO pio, uint sm){
    pio_neo=pio;
    sm_neo=sm;
}
void neopixel::put_pixel(int pixel_grb) {
    pio_sm_put_blocking(pio_neo, sm_neo, pixel_grb << 8u);
    return;
}
uint32_t neopixel::urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
    return
            ((uint32_t) (r) << 8) |
            ((uint32_t) (g) << 16) |
            (uint32_t) (b);
}
