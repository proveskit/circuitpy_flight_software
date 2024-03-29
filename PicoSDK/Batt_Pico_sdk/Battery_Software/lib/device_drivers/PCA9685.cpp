#include "PCA9685.h"

PCA9685::PCA9685(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void PCA9685::configure() {
    // Mode1 register: Set to normal mode, enable auto-increment
    writeRegister(0x00, 0x20);

    // Mode2 register: Set to outputs only, invert outputs
    writeRegister(0x01, 0x04);
}

void PCA9685::toggleOutputs(bool state) {
    uint8_t mode1 = readRegister(0x00);
    if (state) {
        // Turn on the OUTDRV bit (bit 4)
        mode1 |= 0x10;
    } else {
        // Turn off the OUTDRV bit (bit 4)
        mode1 &= ~0x10;
    }
    writeRegister(0x00, mode1);
}

void PCA9685::setDutyCycle(uint8_t port, uint16_t duty_cycle) {
    if (port > 15) {
        // Invalid port number, do nothing
        return;
    }

    // Set the LED ON and OFF registers for the specified port
    writeRegister(0x06 + 4 * port, 0x00);              // LEDn_ON_L
    writeRegister(0x07 + 4 * port, 0x00);              // LEDn_ON_H
    writeRegister(0x08 + 4 * port, duty_cycle & 0xFF); // LEDn_OFF_L
    writeRegister(0x09 + 4 * port, duty_cycle >> 8);   // LEDn_OFF_H
}

void PCA9685::setPortState(uint8_t port, bool state) {
    if (port > 15) {
        // Invalid port number, do nothing
        return;
    }

    // Set the LED ON and OFF registers to turn on or off the specified port
    if (state) {
        // Turn on the specified port
        setDutyCycle(port, 4095); // Set to full brightness
    } else {
        // Turn off the specified port
        setDutyCycle(port, 0); // Set to minimum brightness (fully off)
    }
}

void PCA9685::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t data[2] = {reg, value};
    i2c_write_blocking(i2c, address, data, 2, false);
}

uint8_t PCA9685::readRegister(uint8_t reg) {
    uint8_t data[1] = {reg};
    i2c_write_blocking(i2c, address, data, 1, true);
    i2c_read_blocking(i2c, address, data, 1, false);
    return data[0];
}