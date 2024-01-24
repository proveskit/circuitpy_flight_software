#include "main.h"

void main_program(neopixel neo){
    sleep_ms(10);
    tools t(true, "[MAIN] ");                                                       //instantiate tools class (set debug mode to true)
    t.debug_print("I am in main!\n");                                               //debug print can toggle print statements for debugging
    neo.put_pixel(neo.urgb_u32(0, 0xff, 0));                                        //makes the neopixel green
    t.debug_print("Initializing Hardware...\n");
    pysquared satellite(neo);
    float data[3]={0,0,0};
    while(true){

        /*
            Hypothetical Code Logic (remove while)
        */
        satellite_functions functions(satellite);
        satellite.all_faces_off();
        sleep_ms(1000);
        satellite.all_faces_on();
        functions.battery_manager(); //method obtains current battery status
        //functions.beacon();
        //functions.listen();
        //uint loiter_time=270;
        //satellite.burn_flag = functions.smart_burn(loiter_time);
        //functions.beacon();
        //functions.listen();
        //satellite.battery_manager();
        //functions.beacon_state_of_health();
        //functions.listen();
        while(true){
            switch(satellite.get_power_mode()){
                case 0:
                    critical_power_operations(t, functions);
                    break;
                case 1:
                    low_power_operations(t, neo, functions);
                    break;
                case 2:
                    normal_power_operations(t, neo, functions);
                    break;
                case 3:
                    maximum_power_operations(t, neo, functions);
                    break;
            }
            satellite.check_reboot();
        }
    }
    return;
}

void critical_power_operations(tools t, satellite_functions functions){
    t.debug_print("Satellite is in critical power mode!\n");
    //functions.beacon();
    //functions.listen();
    //functions.beacon_state_of_health();
    //functions.listen();
    //functions.long_hybernate();
    return;
}

void low_power_operations(tools t, neopixel neo, satellite_functions functions){
    t.debug_print("Satellite is in low power mode!\n");
    neo.put_pixel(neo.urgb_u32(0xFF,0x00,0x00));
    //functions.beacon();
    //functions.listen();
    //functions.beacon_state_of_health();
    //functions.listen();
    //functions.short_hybernate();
}

void normal_power_operations(tools t, neopixel neo, satellite_functions functions){
    t.debug_print("Satellite is in normal power mode!\n");
    neo.put_pixel(neo.urgb_u32(0xFF,0xFF,0x00));
    functions.battery_manager();
    sleep_ms(1000);
    functions.all_face_data();
    //maybe consider tasking second core to stuff
}

void maximum_power_operations(tools t, neopixel neo, satellite_functions functions){
    t.debug_print("Satellite is in maximum power mode!\n");
    neo.put_pixel(neo.urgb_u32(0x00,0xFF,0x00));
    functions.battery_manager();
    sleep_ms(1000);
    functions.all_face_data();
    //maybe consider tasking second core to stuff
}