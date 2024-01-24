#include "PCT2075.h"

PCT2075::PCT2075(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void PCT2075::configure() {
    // Configuration Register (example settings, adjust based on your requirements)
    // Set conversion rate to 4Hz (bits 7 and 6), and enable alert mode (bit 4)
    writeRegister(0x01, 0x90);
}

float PCT2075::readTemperature() {
    uint16_t rawTemperature = readRegister(0x00);
    float temperature;
    if (rawTemperature>=32768){
        rawTemperature-=32768;
        rawTemperature=rawTemperature>>5;
        // PCT2075 temperature is in 12-bit format with a resolution of 0.125 degrees Celsius per LSB
        temperature = static_cast<float>(rawTemperature) * -0.125f;
    }
    else{
        rawTemperature=rawTemperature>>5;
        // PCT2075 temperature is in 12-bit format with a resolution of 0.125 degrees Celsius per LSB
        temperature = static_cast<float>(rawTemperature) * 0.125f;
    }
    return temperature;
}

void PCT2075::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t data[2] = {reg, value};
    i2c_write_blocking(i2c, address, data, 2, false);
}

uint16_t PCT2075::readRegister(uint8_t reg) {
    uint8_t data[2] = {reg};
    i2c_write_blocking(i2c, address, data, 1, true);
    i2c_read_blocking(i2c, address, data, 2, false);
    return (data[0] << 8) | data[1];
}