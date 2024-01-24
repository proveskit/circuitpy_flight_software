#include "pico/stdlib.h"
#include "hardware/i2c.h"

class DRV2605 {
public:
    DRV2605(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();
    void setMode(uint8_t mode);
    void setWaveform(uint8_t waveform);
    void setLibrary(uint8_t library);
    void setEffect(uint8_t effect);
    void start();
    void stop();

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint8_t value);
};