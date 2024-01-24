#include "INA219.h"

INA219::INA219(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void INA219::configure() {
    // Configuration Register (default values for now)
    uint16_t config = 0x019F;  // 32V, 1A, Continuous Shunt and Bus, 12-bit resolution
    writeRegister(0x00, config);
    calibrate(32.767,12);
}

float INA219::readShuntVoltage() {
    int16_t value = readRegister(0x01);
    return value * 0.00001;  // LSB = 10uV
}

float INA219::readBusVoltage() {
    uint16_t value = readRegister(0x02);
    // Shift right to get rid of the reserved bits, then multiply by 4 to get mV
    return (value >> 3) * 0.004;
}

float INA219::readCurrent() {
    int16_t value = readRegister(0x04);
    return value;  // LSB = 1mA
}

void INA219::calibrate(float max_current_amps, float max_voltage) {
    // Calculate the calibration values for microamp measurements
    // See the datasheet for the formulas and additional details
    float current_lsb = max_current_amps / 32767.0;  // Current LSB

    // Set calibration register
    uint16_t calibration_value = static_cast<uint16_t>(0.04096 / (current_lsb * 0.002));
    writeRegister(0x05, calibration_value);
}

void INA219::writeRegister(uint8_t reg, uint16_t value) {
    uint8_t data[3];
    data[0] = reg;
    data[1] = (value >> 8) & 0xFF;
    data[2] = value & 0xFF;
    i2c_write_blocking(i2c, address, data, 3, false);
}

uint16_t INA219::readRegister(uint8_t reg) {
    uint8_t data[2];
    i2c_write_blocking(i2c, address, &reg, 1, true);
    i2c_read_blocking(i2c, address, data, 2, false);
    return (data[0] << 8) | data[1];
}