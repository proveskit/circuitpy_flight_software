#include "ADS1015.h"

ADS1015::ADS1015(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void ADS1015::configure() {
    // Configuration Register (example settings, adjust based on your requirements)
    // Set the operational status (bit 15) to start a single conversion
    // Set the input multiplexer configuration (bits 14, 13, 12) for the desired channel
    // Set the gain (bits 11, 10, 9) for the desired voltage range
    writeRegister(0x01, 0x8000 | (0x4000) | (0x0200));
}

int16_t ADS1015::readSingleEnded(uint8_t channel) {
    if (channel > 3) {
        // Invalid channel, return an error value
        return -1;
    }

    // Configure the input multiplexer for the specified channel
    uint16_t config = 0xC000 | (channel << 12) | (0x0400);
    writeRegister(0x01, config);

    // Wait for conversion to complete (bit 15 in the configuration register)
    while (readRegister(0x01) & 0x8000) {
        // Wait
    }

    // Read the conversion result from the conversion register
    uint16_t result = readRegister(0x00);

    // Convert the 12-bit result to a signed 16-bit value
    int16_t value = static_cast<int16_t>(result) >> 4;

    return value;
}

void ADS1015::writeRegister(uint8_t reg, uint16_t value) {
    uint8_t data[3] = {reg, static_cast<uint8_t>((value >> 8) & 0xFF), static_cast<uint8_t>(value & 0xFF)};
    i2c_write_blocking(i2c, address, data, 3, false);
}

uint16_t ADS1015::readRegister(uint8_t reg) {
    uint8_t data[2] = {reg};
    i2c_write_blocking(i2c, address, data, 1, true);
    i2c_read_blocking(i2c, address, data, 2, false);
    return (data[0] << 8) | data[1];
}