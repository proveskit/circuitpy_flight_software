#include "tools.h"

tools::tools(bool print, const char* prog){
    debug=print;
    program=prog;
}
void tools::debug_print(const char* message){
    if(debug){
        uint32_t sec_since_boot = to_ms_since_boot(get_absolute_time())/1000;
        uint32_t min_since_boot = sec_since_boot/60;
        uint secs = sec_since_boot%60;
        uint mins = min_since_boot%60;
        uint hours = min_since_boot/60;
        printf("%02d:%02d:%02d ",hours,mins,secs);
        printf(program);
        printf(message);
    }
}
void tools::i2c_scan(i2c_inst_t *i2c){
    printf("\nI2C Bus Scan\n");
    printf("   0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n");
    for (int addr = 0; addr < (1 << 7); ++addr) {
        if (addr % 16 == 0) {
            printf("%02x ", addr);
        }

        // Perform a 1-byte dummy read from the probe address. If a slave
        // acknowledges this address, the function returns the number of bytes
        // transferred. If the address byte is ignored, the function returns
        // -1.

        // Skip over any reserved addresses.
        int ret;
        uint8_t rxdata;
        ret = i2c_read_timeout_us(i2c, addr, &rxdata, 1, false, 100000);

        printf(ret < 0 ? "." : "@");
        printf(addr % 16 == 15 ? "\n" : "  ");
    }
}