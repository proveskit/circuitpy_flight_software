#include "MCP9808.h"

MCP9808::MCP9808(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void MCP9808::configure() {
    // Configuration Register (example settings, adjust based on your requirements)
    // Set resolution to 0.0625 degrees Celsius per LSB (bits 9, 10, and 11)
    writeRegister(0x01, 0x0600);
}

float MCP9808::readTemperature() {
    uint16_t rawTemperature = readRegister(0x05);
    // MCP9808 temperature is in 13-bit format with a resolution of 0.0625 degrees Celsius per LSB
    float temperature = static_cast<float>(rawTemperature & 0x0FFF) * 0.0625f;
    
    // Check sign bit (bit 12)
    if (rawTemperature & 0x1000) {
        // Temperature is negative, apply two's complement
        temperature -= 256.0f;
    }

    return temperature;
}

void MCP9808::writeRegister(uint8_t reg, uint16_t value) {
    uint8_t data[3] = {reg, static_cast<uint8_t>((value >> 8) & 0xFF), static_cast<uint8_t>(value & 0xFF)};
    i2c_write_blocking(i2c, address, data, 3, false);
}

uint16_t MCP9808::readRegister(uint8_t reg) {
    uint8_t data[2] = {reg};
    i2c_write_blocking(i2c, address, data, 1, true);
    i2c_read_blocking(i2c, address, data, 2, false);
    return (data[0] << 8) | data[1];
}