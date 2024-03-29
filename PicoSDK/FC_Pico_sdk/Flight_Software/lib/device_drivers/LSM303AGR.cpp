#include "LSM303AGR.h"

LSM303AGR_ACCEL::LSM303AGR_ACCEL(i2c_inst_t *i2c, uint8_t ADDR_ACCEL){
    i2c_accel=i2c;
    _ADDRESS_ACCEL=ADDR_ACCEL;
}

void LSM303AGR_ACCEL::init(){
    _reg_read(i2c_accel, _ADDRESS_ACCEL, _REG_ACCEL_WHO_AM_I, buf, 1);
    if(buf[0] != ACCEL_ID){
        throw("LSM303AGR_ACCEL Device Initialization failed!\n");
    }
}

float LSM303AGR_ACCEL::_scale_data(float data){

    return 0;
}

float LSM303AGR_ACCEL::_lsb_shift(){
    return 0;
}

int LSM303AGR_ACCEL::_reg_read(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes){
    int num_bytes_read = 0;

    // Check to make sure caller is asking for 1 or more bytes
    if (nbytes < 1) {
        return 0;
    }

    // Read data from register(s) over I2C
    i2c_write_blocking(i2c, addr, &reg, 1, true);
    num_bytes_read = i2c_read_blocking(i2c, addr, buf, nbytes, false);

    return num_bytes_read;
}

void LSM303AGR_ACCEL::_reg_write(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes){
    uint8_t msg[nbytes + 1];

    // Check to make sure caller is sending 1 or more bytes
    if (nbytes < 1) {
        return;
    }

    // Append register address to front of data packet
    msg[0] = reg;
    for (int i = 0; i < nbytes; i++) {
        msg[i + 1] = buf[i];
    }

    // Write data to register(s) over I2C
    i2c_write_blocking(i2c, addr, msg, (nbytes + 1), false);

    return;
}

void LSM303AGR_ACCEL::raw_acceleration(int16_t *data){
    _reg_read(i2c_accel, _ADDRESS_ACCEL, _REG_ACCEL_OUT_X_H_A, buf, 2);
    data[0]= (int16_t)((buf[0]<<8)|buf[1]);
    _reg_read(i2c_accel, _ADDRESS_ACCEL, _REG_ACCEL_OUT_Y_H_A, buf, 2);
    data[1]= (int16_t)((buf[0]<<8)|buf[1]);
    _reg_read(i2c_accel, _ADDRESS_ACCEL, _REG_ACCEL_OUT_Z_H_A, buf, 2);
    data[2]= (int16_t)((buf[0]<<8)|buf[1]);
    return;
}

float* LSM303AGR_ACCEL::acceleration(){

    return 0;
}



LSM303AGR_MAG::LSM303AGR_MAG(i2c_inst_t *i2c, uint8_t ADDR_MAG){
    i2c_mag=i2c;
    _ADDRESS_MAG=ADDR_MAG;
}

void LSM303AGR_MAG::init(){
    _reg_write(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_A_M, (uint8_t*)0x20,1);
    sleep_ms(100);
    _reg_write(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_A_M, (uint8_t*)0x40, 1);
    sleep_ms(100);
    _reg_write(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_A_M, (uint8_t*)0x80, 1);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_A_M, buf, 1);
    _reg_write(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_A_M, (uint8_t*)(((int)buf & 0xFC)|0x0C), 1);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_C_M, buf, 1);
    _reg_write(i2c_mag, _ADDRESS_MAG, _REG_MAG_CFG_C_M, (uint8_t*)((int)buf | 0x10), 1);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_WHO_AM_I, buf, 1);
    if(buf[0] != MAG_ID){
        throw("LSM303AGR_MAG Device Initialization failed!\n");
    }
}

int LSM303AGR_MAG::_reg_read(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes){
    int num_bytes_read = 0;

    // Check to make sure caller is asking for 1 or more bytes
    if (nbytes < 1) {
        return 0;
    }

    // Read data from register(s) over I2C
    i2c_write_blocking(i2c, addr, &reg, 1, true);
    num_bytes_read = i2c_read_blocking(i2c, addr, buf, nbytes, false);

    return num_bytes_read;
}

void LSM303AGR_MAG::_reg_write(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes){
    uint8_t msg[nbytes + 1];

    // Check to make sure caller is sending 1 or more bytes
    if (nbytes < 1) {
        return;
    }

    // Append register address to front of data packet
    msg[0] = reg;
    for (int i = 0; i < nbytes; i++) {
        msg[i + 1] = buf[i];
    }

    // Write data to register(s) over I2C
    i2c_write_blocking(i2c, addr, msg, (nbytes + 1), false);

    return;
}

void LSM303AGR_MAG::raw_mag(float *mag_data){
    uint16_t data[3];
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OUT_X_L_M, buf, 2);
    data[0]= (uint16_t)((buf[1]<<8)|buf[0]);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OUT_Y_L_M, buf, 2);
    data[1]= (uint16_t)((buf[1]<<8)|buf[0]);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OUT_Z_L_M, buf, 2);
    data[2]= (uint16_t)((buf[1]<<8)|buf[0]);
    for(int i = 0; i < 3; i++){
        data[i]*=-1;
        mag_data[i]=((float)data[i])*0.15;
    }
    return;
}

void LSM303AGR_MAG::calibrated_mag(float *mag_data){
    uint16_t data[3];
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OFFSET_X_L_M, buf, 2);
    data[0]= (uint16_t)((buf[1]<<8)|buf[0]);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OFFSET_Y_L_M, buf, 2);
    data[1]= (uint16_t)((buf[1]<<8)|buf[0]);
    _reg_read(i2c_mag, _ADDRESS_MAG, _REG_MAG_OFFSET_Z_L_M, buf, 2);
    data[2]= (uint16_t)((buf[1]<<8)|buf[0]);
    raw_mag(mag_data);
    for(int i = 0; i < 3; i++){
        data[i]*=-1;
        mag_data[i]-=((float)data[i])*0.15;
    }

}
