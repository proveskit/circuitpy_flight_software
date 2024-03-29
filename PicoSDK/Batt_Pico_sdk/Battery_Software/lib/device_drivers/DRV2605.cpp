#include "DRV2605.h"

DRV2605::DRV2605(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    i2c = i2c_instance;
    address = i2c_address;
}

void DRV2605::configure() {
    // Basic configuration, adjust based on your requirements
    // This example assumes default settings for simplicity
    // Refer to the DRV2605 datasheet for detailed register configurations
    writeRegister(0x01, 0x09); // Set to internal trigger mode
}

void DRV2605::setMode(uint8_t mode) {
    // Set the operating mode (Mode register)
    writeRegister(0x01, mode);
}

void DRV2605::setWaveform(uint8_t waveform) {
    // Set the waveform sequence (Waveform register)
    writeRegister(0x04, waveform);
}

void DRV2605::setLibrary(uint8_t library) {
    // Set the library selection (Library Selection register)
    writeRegister(0x05, library);
}

void DRV2605::setEffect(uint8_t effect) {
    // Set the effect selection (Waveform Sequencer register)
    writeRegister(0x06, effect);
}

void DRV2605::start() {
    // Trigger the device to start playing the configured effect
    // (Control register - GO bit)
    writeRegister(0x0C, 0x80);
}

void DRV2605::stop() {
    // Stop the playback and clear the GO bit
    writeRegister(0x0C, 0x00);
}

void DRV2605::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t data[2] = {reg, value};
    i2c_write_blocking(i2c, address, data, 2, false);
}