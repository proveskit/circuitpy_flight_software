#include "VEML7700.h"

VEML7700::VEML7700(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void VEML7700::configure() {
    // Configuration Register (example settings, adjust based on your requirements)
    // Set integration time to 100 ms (bits 11, 10, and 9)
    // Enable high dynamic range mode (bit 6)
    // Enable auto-gain (bit 5)
    writeRegister(0x00, 0x10C0);
}

uint16_t VEML7700::readAmbientLight() {
    // Read the ambient light level from the result register
    return readRegister(0x04);
}

void VEML7700::writeRegister(uint8_t reg, uint16_t value) {
    uint8_t data[3] = {reg, static_cast<uint8_t>((value >> 8) & 0xFF), static_cast<uint8_t>(value & 0xFF)};
    i2c_write_blocking(i2c, address, data, 3, false);
}

uint16_t VEML7700::readRegister(uint8_t reg) {
    uint8_t data[2] = {reg};
    i2c_write_blocking(i2c, address, data, 1, true);
    i2c_read_blocking(i2c, address, data, 2, false);
    return (data[0] << 8) | data[1];
}