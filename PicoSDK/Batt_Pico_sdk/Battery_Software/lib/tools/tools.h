#ifndef _TOOLS_H
#define _TOOLS_H
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/timer.h"
#include "hardware/i2c.h"
class tools{
public:
    bool debug;
    const char* program;
    tools(bool print, const char* prog);
    void debug_print(const char* message);
    void i2c_scan(i2c_inst_t *i2c);
};
#endif