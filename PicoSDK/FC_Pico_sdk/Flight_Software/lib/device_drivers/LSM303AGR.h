#ifndef _LSM303AGR_H
#define _LSM303AGR_H
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

class LSM303AGR_ACCEL{
private:
    i2c_inst_t *i2c_accel;
    uint8_t _ADDRESS_ACCEL;
    uint8_t ACCEL_ID = 0x33;
    /*
        Registers
    */
    uint8_t _REG_ACCEL_WHO_AM_I=0x0F;
    uint8_t _REG_ACCEL_CTRL_REG1_A=0x20;
    uint8_t _REG_ACCEL_CTRL_REG2_A=0x21;
    uint8_t _REG_ACCEL_CTRL_REG3_A=0x22;
    uint8_t _REG_ACCEL_CTRL_REG4_A=0x23;
    uint8_t _REG_ACCEL_CTRL_REG5_A=0x24;
    uint8_t _REG_ACCEL_CTRL_REG6_A=0x25;
    uint8_t _REG_ACCEL_REFERENCE_A=0x26;
    uint8_t _REG_ACCEL_STATUS_REG_A=0x27;
    uint8_t _REG_ACCEL_OUT_X_L_A=0x28;
    uint8_t _REG_ACCEL_OUT_X_H_A=0x29;
    uint8_t _REG_ACCEL_OUT_Y_L_A=0x2A;
    uint8_t _REG_ACCEL_OUT_Y_H_A=0x2B;
    uint8_t _REG_ACCEL_OUT_Z_L_A=0x2C;
    uint8_t _REG_ACCEL_OUT_Z_H_A=0x2D;
    uint8_t _REG_ACCEL_FIFO_CTRL_REG_A=0x2E;
    uint8_t _REG_ACCEL_FIFO_SRC_REG_A=0x2F;
    uint8_t _REG_ACCEL_INT1_CFG_A=0x30;
    uint8_t _REG_ACCEL_INT1_SOURCE_A=0x31;
    uint8_t _REG_ACCEL_INT1_THS_A=0x32;
    uint8_t _REG_ACCEL_INT1_DURATION_A=0x33;
    uint8_t _REG_ACCEL_INT2_CFG_A=0x34;
    uint8_t _REG_ACCEL_INT2_SOURCE_A=0x35;
    uint8_t _REG_ACCEL_INT2_THS_A=0x36;
    uint8_t _REG_ACCEL_INT2_DURATION_A=0x37;
    uint8_t _REG_ACCEL_CLICK_CFG_A=0x38;
    uint8_t _REG_ACCEL_CLICK_SRC_A=0x39;
    uint8_t _REG_ACCEL_CLICK_THS_A=0x3A;
    uint8_t _REG_ACCEL_TIME_LIMIT_A=0x3B;
    uint8_t _REG_ACCEL_TIME_LATENCY_A=0x3C;
    uint8_t _REG_ACCEL_TIME_WINDOW_A=0x3D;
    uint8_t _REG_ACCEL_ACT_THS_A=0x3E;
    uint8_t _REG_ACCEL_ACT_DUR_A=0x3F;
    /*
        Class specific variables for handling data
    */
    uint8_t buf[2];
    /*
        Class specific functions for handling register reading and writing
    */
    float _scale_data(float data);
    float _lsb_shift();
    int _reg_read(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes);
    void _reg_write(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes);
public:

    LSM303AGR_ACCEL(i2c_inst_t *i2c=i2c_default, uint8_t ADDR_ACCEL=0x19);

    void init();
    void raw_acceleration(int16_t *data);    
    float* acceleration();

};

class LSM303AGR_MAG{
private:
    i2c_inst_t *i2c_mag;
    uint8_t _ADDRESS_MAG;
    uint8_t MAG_ID = 0x40;
    /*
        Registers
    */
    uint8_t _REG_MAG_WHO_AM_I=0x4F;
    uint8_t _REG_MAG_OFFSET_X_L_M=0x45;
    uint8_t _REG_MAG_OFFSET_X_H_M=0x46;
    uint8_t _REG_MAG_OFFSET_Y_L_M=0x47;
    uint8_t _REG_MAG_OFFSET_Y_H_M=0x48;
    uint8_t _REG_MAG_OFFSET_Z_L_M=0x49;
    uint8_t _REG_MAG_OFFSET_Z_H_M=0x4A;
    uint8_t _REG_MAG_CFG_A_M=0x60;
    uint8_t _REG_MAG_CFG_B_M=0x61;
    uint8_t _REG_MAG_CFG_C_M=0x62;
    uint8_t _REG_MAG_INT_CTRL_M=0x63;
    uint8_t _REG_MAG_INT_SOURCE_M=0x64;
    uint8_t _REG_MAG_INT_THS_L_M=0x65;
    uint8_t _REG_MAG_INT_THS_H_M=0x66;
    uint8_t _REG_MAG_STATUS_REG_M=0x67;
    uint8_t _REG_MAG_OUT_X_L_M=0x68;
    uint8_t _REG_MAG_OUT_X_H_M=0x69;
    uint8_t _REG_MAG_OUT_Y_L_M=0x6A;
    uint8_t _REG_MAG_OUT_Y_H_M=0x6B;
    uint8_t _REG_MAG_OUT_Z_L_M=0x6C;
    uint8_t _REG_MAG_OUT_Z_H_M=0x6D;
    /*
        Class specific variables for handling data
    */
    uint8_t buf[2];
    /*
        Class specific functions for handling register reading and writing
    */
    int _reg_read(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes);
    void _reg_write(i2c_inst_t *i2c, const uint8_t addr, const uint8_t reg, uint8_t *buf, const uint8_t nbytes);
public:

    LSM303AGR_MAG(i2c_inst_t *i2c=i2c_default, uint8_t ADDR_MAG=0x1E);

    void init();
    void raw_mag(float *mag_data);    
    void calibrated_mag(float *mag_data);

};
#endif