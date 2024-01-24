#include "functions.h"

satellite_functions::satellite_functions(pysquared& satellite):t(true, "[FUNCTIONS] "), c(satellite), b(i2c0, c.i2c_mux){
    t.debug_print("Functions initialized\n");
}

void satellite_functions::battery_manager(){
    float internal_temp = c.get_internal_temp();
    float battery_temp = c.get_thermocouple_temp();
    float battery_voltage = c.get_battery_voltage();
    float draw_current = c.get_draw_current();
    float charge_voltage = c.get_charge_voltage();
    float charge_current = c.get_charge_current();
    printf("Internal Temperature: %.3fC\n",internal_temp);
    printf("Battery Temperature: %.3fC\n",battery_temp);
    printf("Battery Voltage: %.3fV\n",battery_voltage);
    printf("Charge Voltage: %.3fV\n",charge_voltage);
    printf("Draw Current: %.3fmA\n",draw_current);
    printf("Charge Current: %.3fmA\n",charge_current);
    if(battery_voltage >= 7.4){c.pwr_mode=3;}
    else if(battery_voltage < 7.4 && battery_voltage >= 6.8){c.pwr_mode=2;}
    else if(battery_voltage < 6.8 && battery_voltage >= 6.4){c.pwr_mode=1;}
    else if(battery_voltage < 6.4){c.pwr_mode=0;}
    if(battery_temp < -10){
        t.debug_print("battery temperature is low, attempting to heat...\n");
        battery_heater();
    }
}

void satellite_functions::battery_heater(){
    //do stuff here
    return;
}

void satellite_functions::all_face_data(){
    float face_temps[5];
    float face_light[5];
    for(uint8_t i = 0; i < 5; i++){
        face_temps[i]=b.getTemperature(i);
        face_light[i]=b.getAmbientLight(i);
        printf("Face %u Temperature: %.3fC\n", i, face_temps[i]);
        printf("Face %u Light: %.3fLux\n", i, face_light[i]);
    }
}