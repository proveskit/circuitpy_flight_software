'''
This is the class that contains all of the functions for our CubeSat. 
We pass the cubesat object to it for the definitions and then it executes 
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
'''
import time
import alarm
import gc
import traceback
import random
from debugcolor import co

class functions:

    def debug_print(self,statement):
        if self.debug:
            print(co("[Functions]" + statement, 'green', 'bold'))
    def __init__(self,cubesat):
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.debug_print("Initializing Functionalities")
        self.Errorcount=0
        self.facestring=[]
        self.jokes=["Hey Its pretty cold up here, did someone forget to pay the electric bill?",
                    "Connect with me on LinkedIn: https://www.linkedin.com/in/ernesto-montes/",
                    "Connect with me on LinkedIn: https://www.linkedin.com/in/ali-i-malik/",
                    "Hey Hey Ho Ho, Coleys got to go",
                    "https://www.proveskit.space",
                    "Sorry, Dr. Ahmadi this satellite has not been wind tunnel tested!",
                    "KN6NAQ did it first lol",
                    "KN6NAQ forgot to save the file",
                    "Hello New York City! Catch you up here later!",
                    "Go Mets!",
                    "Insert one liner here",
                    "Sometimes maybe gabba, sometimes maybe gool",
                    "I saw the BLV from up here, he was waving to me :)",
                    "I cost 20.83 percent of a 1977 Porsche 924 to make",
                    "This is a BroncoSpace educational product. For instructional use only",
                    "PROP65 WARNING: This product is known to the state of California to contain materials that may cause cancer or birth defects.",
                    "s/o my boi Mikey B",
                    "it is 12:14am in da lab rn",
                    "Help, I am falling and I cannot get up",
                    "You have 7 degrees and none of them are in chemistry",
                    "Launcher? I hardly know her",
                    "With all this radiation, when do I turn into the Hulk?",
                    "I would not be possible without 60 grit sandpaper",
                    "Big smallsats during the week, small smallsats during the weekend",
                    "so Im getting paid for this, right?",
                    "Yeah, so like building smallsats is really just a hobby for me. If I dont want to do it, I dont have to",
                    "Just dodged a gamma ray lol",
                    "Wherever you go, there you are",
                    "And on the third day, the satellite rose again! Whats up Vatican City!",
                    "Be Aware of Snake, Traveller Snake No Harm You, Snake Aware of You",
                    "Hey guys, I just checked and the world is round!",
                    "Hey Siri, play We are Finally Landing By Home",
                    "Did you know: Crowbars were invented in 1748. Before then crows mostly drank alone",
                    "I had a long fungi joke, but I dont have enough SHROOM to downlink it",
                    "What is a mushrooms favorite thing to bring camping? Spores!",
                    "Im throwing a party in space. Can you help me planet?",
                    "What happens when someone slaps you at a high frequency? It Hertz!",
                    "Uke, I am your father - an acoustic guitar to a ukelele",
                    "I went through 20Gs of vibration for this!?",
                    "What is your purpose? you tell us your temperature... Oh My God ",
                    "What kind of sharks do carpenters like best? The hammerhead and saw shark!",
                    "I checked out a book on anti-gravity, now I cant put it down!",
                    "Whats E.T. short for? He has little legs",
                    "Did you hear the moon needs money? Its on its last quarter",
                    "In another life, I would have really loved just doing laundry and taxes with you",
                    "What do astronomers do when they finish calculating the time from sun up to sun down? They call it a day!",
                    "Is this enough social distancing? This feels a little far"]
        self.last_battery_temp = 20
        self.state_bool=False
        self.face_data_baton = False
        self.detumble_enable_z = True
        self.detumble_enable_x = True
        self.detumble_enable_y = True
        try:
            self.cubesat.all_faces_on()
        except Exception as e:
            self.debug_print("Couldn't turn faces on: " + ''.join(traceback.format_exception(e)))
    
    '''
    Satellite Management Functions
    '''
    def battery_heater(self):
        """
        Battery Heater Function reads temperature at the end of the thermocouple and tries to 
        warm the batteries until they are roughly +4C above what the batteries should normally sit(this 
        creates a band stop in which the battery heater never turns off) The battery heater should not run
        forever, so a time based stop is implemented
        """
        try:
            
            ThermoTemp=self.cubesat.IMU.mcp.temperature
            
            if ThermoTemp < self.cubesat.NORMAL_BATT_TEMP:
                end_time=0
                self.cubesat.heater_on()
                while ThermoTemp < self.cubesat.NORMAL_BATT_TEMP+4 and end_time<5:
                    time.sleep(1)
                    ThermoTemp=self.cubesat.IMU.mcp.temperature
                    end_time+=1
                    self.debug_print(str(f"Heater has been on for {end_time} seconds and the battery temp is {ThermoTemp}C"))
                self.cubesat.heater_off()
                return True
            else: 
                self.debug_print("Battery is already warm enough")
                return False
        except Exception as e:
            self.cubesat.heater_off()
            self.debug_print("Error Initiating Battery Heater" + ''.join(traceback.format_exception(e)))
            return False
        finally:
            self.cubesat.heater_off()
    
    def current_check(self):
        return self.cubesat.current_draw
    
    def test_faces(self):    
        try:
            self.cubesat.all_faces_on()
            a = self.all_face_data()
            
            self.last_battery_temp= a[4][2][0]-a[4][2][2]
            if self.last_battery_temp is not None:
                
                #Iterate through a and determine if any of the values are None
                #Add a counter to keep track of which iternation we are on
                count = 0 
                for face in a:
                    if len(face) == 0:
                        self.debug_print("Face " + str(count) + " is None")
                        self.cubesat.hardware[f'Face{count}'] = False
                        count += 1
                    else:
                        self.cubesat.hardware[f'Face{count}'] = True
                        count += 1
                
                self.debug_print(str(self.cubesat.hardware))
            else:
                self.debug_print("Battery temperature is not valid")
            
            del a
        except Exception as e:
            self.debug_print("An Error occured while trying to test faces: " + ''.join(traceback.format_exception(e)))

    '''
    Radio Functions
    '''  
    def send(self,msg):
        """Calls the RFM9x to send a message. Currently only sends with default settings.
        
        Args:
            msg (String,Byte Array): Pass the String or Byte Array to be sent. 
        """
        import Field
        self.field = Field.Field(self.cubesat,self.debug)
        message="KN6NAT " + str(msg) + " KN6NAT"
        self.field.Beacon(message)
        if self.cubesat.f_fsk:
            self.cubesat.radio1.cw(message)
        self.debug_print(f"Sent Packet: " + message)
        del self.field
        del Field

    def beacon(self):
        """Calls the RFM9x to send a beacon. """
        import Field
        try:
            lora_beacon = "KN6NAT Hello I am Yearling^2! I am in: " + str(self.cubesat.power_mode) +" power mode. V_Batt = " + str(self.cubesat.battery_voltage) + "V. IHBPFJASTMNE! KN6NAT"
        except Exception as e:
            self.debug_print("Error with obtaining power data: " + ''.join(traceback.format_exception(e)))
            lora_beacon = "KN6NAT Hello I am Yearling^2! I am in: " + "an unidentified" +" power mode. V_Batt = " + "Unknown" + ". IHBPFJASTMNE! KN6NAT"

        self.field = Field.Field(self.cubesat,self.debug)
        self.field.Beacon(lora_beacon)
        if self.cubesat.f_fsk:
            self.cubesat.radio1.cw(lora_beacon)
        del self.field
        del Field
    
    def joke(self):
        self.send(random.choice(self.jokes))
    

    def state_of_health(self):
        import Field
        self.test_faces()
        self.state_list=[]
        #list of state information 
        try:
            self.state_list = [
                f"PM:{self.cubesat.power_mode}",
                f"VB:{self.cubesat.battery_voltage}",
                f"ID:{self.cubesat.current_draw}",
                f"VS:{self.cubesat.system_voltage}",
                f"UT:{self.cubesat.uptime}",
                f"BN:{self.cubesat.c_boot}",
                f"MT:{self.cubesat.micro.cpu.temperature}",
                f"RT:{self.cubesat.radio1.former_temperature}",
                f"AT:{self.cubesat.IMU.mcp.ambient_temperature}",
                f"BT:{self.cubesat.IMU.mcp.temperature}",
                f"AB:{int(self.cubesat.burned)}",
                f"BO:{int(self.cubesat.f_brownout)}",
                f"FK:{int(self.cubesat.f_fsk)}"
            ]
        except Exception as e:
            self.debug_print("Couldn't aquire data for the state of health: " + ''.join(traceback.format_exception(e)))
        
        self.field = Field.Field(self.cubesat,self.debug)
        if not self.state_bool:
            self.field.Beacon("KN6NAT Yearling^2 State of Health 1/2" + str(self.state_list)+ "KN6NAT")
            if self.cubesat.f_fsk:
                self.cubesat.radio1.cw("KN6NAT Yearling^2 State of Health 1/2" + str(self.state_list)+ "KN6NAT")
            self.state_bool=True
        else:
            self.field.Beacon("KN6NAT YSOH 2/2" + str(self.cubesat.hardware) +"KN6NAT")
            if self.cubesat.f_fsk:
                self.cubesat.radio1.cw("KN6NAT YSOH 2/2" + str(self.cubesat.hardware) +"KN6NAT")
            self.state_bool=False
        del self.field
        del Field

    def send_face(self):
        """Calls the data transmit function from the field class
        """
        import Field
        self.field = Field.Field(self.cubesat,self.debug)
        self.debug_print("Sending Face Data")
        self.field.Beacon(f'KN6NAT Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} KN6NAT')
        if self.cubesat.f_fsk:
                self.cubesat.radio1.cw(f'KN6NAT Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} KN6NAT')
        del self.field
        del Field
    
    def send_face_data_small(self):
        self.debug_print("Trying to get the data! ")
        data = self.all_face_data()
        i = 0
        try:
            for face in data:
                self.debug_print(face)
                self.cubesat.radio1.send("Face Data: " + str(i) + " " + str(face))
                i+=1
            return True
        except Exception as e:
            self.debug_print("Error sending face data: " + ''.join(traceback.format_exception(e)))
            return False
    
    def listen(self):
        import cdh
        #This just passes the message through. Maybe add more functionality later. 
        try:
            self.debug_print("Listening")
            self.cubesat.radio1.receive_timeout=10
            received = self.cubesat.radio1.receive(keep_listening=True)
        except Exception as e:
            self.debug_print("An Error has occured while listening: " + ''.join(traceback.format_exception(e)))
            received=None
        try:
            if received is not None:
                self.debug_print("Recieved Packet: "+str(received))
                cdh.message_handler(self.cubesat,received)
                return True
        except Exception as e:
            self.debug_print("An Error has occured while handling command: " + ''.join(traceback.format_exception(e)))
        del cdh
        
        return False
    
    def listen_joke(self):
        try:
            self.debug_print("Listening")
            self.cubesat.radio1.receive_timeout=10
            received = self.cubesat.radio1.receive(keep_listening=True)
            if "HAHAHAHAHA!" in received:
                return True
            else:
                return False
        except Exception as e:
            self.debug_print("An Error has occured while listening: " + ''.join(traceback.format_exception(e)))
            received=None
            return False

    '''
    Big_Data Face Functions
    change to remove fet values, move to pysquared
    '''  
    def face_toggle(self,face,state):
        dutycycle = 0x0000
        if state:
            duty_cycle=0xffff
        
        if   face == "Face0": self.cubesat.Face0.duty_cycle = duty_cycle      
        elif face == "Face1": self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face2": self.cubesat.Face0.duty_cycle = duty_cycle      
        elif face == "Face3": self.cubesat.Face0.duty_cycle = duty_cycle           
        elif face == "Face4": self.cubesat.Face0.duty_cycle = duty_cycle          
        elif face == "Face5": self.cubesat.Face0.duty_cycle = duty_cycle
    
    def all_face_data(self):
        
        self.cubesat.all_faces_on()
        try:
            import Big_Data
            a = Big_Data.AllFaces(self.debug,self.cubesat.tca)
            
            self.facestring = a.Face_Test_All()
            
            del a
            del Big_Data
        except Exception as e:
            self.debug_print("Big_Data error" + ''.join(traceback.format_exception(e)))
        
        return self.facestring
    
    def get_imu_data(self):
        
        self.cubesat.all_faces_on()
        try:
            data=[]
            data.append(self.cubesat.IMU.Acceleration)
            data.append(self.cubesat.IMU.Gyroscope)
            data.append(self.cubesat.IMU.Magnetometer)
        except Exception as e:
            self.debug_print("Error retrieving IMU data" + ''.join(traceback.format_exception(e)))
        
        return data
    
    def OTA(self):
        # resets file system to whatever new file is received
        pass

    '''
    Logging Functions
    '''  
    def log_face_data(self,data):
        
        self.debug_print("Logging Face Data")
        try:
                self.cubesat.Face_log(data)
        except:
            try:
                self.cubesat.new_file(self.cubesat.Facelogfile)
            except Exception as e:
                self.debug_print('SD error: ' + ''.join(traceback.format_exception(e)))
        
    def log_error_data(self,data):
        
        self.debug_print("Logging Error Data")
        try:
                self.cubesat.log(data)
        except:
            try:
                self.cubesat.new_file(self.cubesat.logfile)
            except Exception as e:
                self.debug_print('SD error: ' + ''.join(traceback.format_exception(e)))
    
    '''
    Misc Functions
    '''  
    #Goal for torque is to make a control system 
    #that will adjust position towards Earth based on Gyro data
    def detumble(self,dur = 7, margin = 0.2, seq = 118):
        self.debug_print("Detumbling")
        self.cubesat.RGB=(255,255,255)
        self.cubesat.all_faces_on()
        try:
            import Big_Data
            a=Big_Data.AllFaces(self.debug, self.cubesat.tca)
        except Exception as e:
            self.debug_print("Error Importing Big Data: " + ''.join(traceback.format_exception(e)))

        try:
            a.sequence=52
        except Exception as e:
            self.debug_print("Error setting motor driver sequences: " + ''.join(traceback.format_exception(e)))
        
        def actuate(dipole,duration):
            #TODO figure out if there is a way to reverse direction of sequence
            if abs(dipole[0]) > 1:
                a.Face2.drive=52
                a.drvx_actuate(duration)
            if abs(dipole[1]) > 1:
                a.Face0.drive=52
                a.drvy_actuate(duration)
            if abs(dipole[2]) > 1:
                a.Face4.drive=52
                a.drvz_actuate(duration)
            
        def do_detumble():
            try:
                import detumble
                for _ in range(3):
                    data=[self.cubesat.IMU.Gyroscope,self.cubesat.IMU.Magnetometer]
                    data[0]=list(data[0])
                    for x in range(3):
                        if data[0][x] < 0.01:
                            data[0][x]=0.0
                    data[0]=tuple(data[0])
                    dipole=detumble.magnetorquer_dipole(data[1],data[0])
                    self.debug_print("Dipole: " + str(dipole))
                    self.send("Detumbling! Gyro, Mag: " + str(data))
                    time.sleep(1)
                    actuate(dipole,dur)
            except Exception as e:
                self.debug_print("Detumble error: " + ''.join(traceback.format_exception(e)))
        try:
            self.debug_print("Attempting")
            do_detumble()
        except Exception as e:
            self.debug_print('Detumble error: ' + ''.join(traceback.format_exception(e)))
        self.cubesat.RGB=(100,100,50)
        
    
    def Short_Hybernate(self):
        self.debug_print("Short Hybernation Coming UP")
        gc.collect()
        #all should be off from cubesat powermode
        self.cubesat.all_faces_off()
        self.cubesat.enable_rf.value=False
        self.cubesat.f_softboot=True
        time.sleep(120)
        self.cubesat.all_faces_on()
        self.cubesat.enable_rf.value=True
        return True
    
    def Long_Hybernate(self):
        self.debug_print("LONG Hybernation Coming UP")
        gc.collect()
        #all should be off from cubesat powermode
        self.cubesat.all_faces_off()
        self.cubesat.enable_rf.value=False
        self.cubesat.f_softboot=True
        time.sleep(600)
        self.cubesat.all_faces_on()
        self.cubesat.enable_rf.value=True
        return True
    