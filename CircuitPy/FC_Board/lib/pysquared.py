"""
CircuitPython driver for PySquared satellite board.
PySquared Hardware Version: mainboard-v01
CircuitPython Version: 8.0.0 alpha
Library Repo:

* Author(s): Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""
# Common CircuitPython Libs
import board, microcontroller
import busio, time, sys, traceback
from storage import mount,umount,VfsFat
import digitalio, sdcardio, pwmio
from debugcolor import co
import gc

# Hardware Specific Libs
import pysquared_rfm9x  # Radio
import neopixel         # RGB LED
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX # IMU
import adafruit_lsm303_accel # Accelerometer

# Common CircuitPython Libs
from os import listdir,stat,statvfs,mkdir,chdir
from bitflags import bitFlag,multiBitFlag,multiByte
from micropython import const


# NVM register numbers
_BOOTCNT  = const(0)
_VBUSRST  = const(6)
_STATECNT = const(7)
_TOUTS    = const(9)
_ICHRG    = const(11)
_DIST     = const(13)
_FLAG     = const(16)

SEND_BUFF=bytearray(252)

class Satellite:
    # General NVM counters
    c_boot      = multiBitFlag(register=_BOOTCNT, lowest_bit=0,num_bits=8)
    c_vbusrst   = multiBitFlag(register=_VBUSRST, lowest_bit=0,num_bits=8)
    c_state_err = multiBitFlag(register=_STATECNT,lowest_bit=0,num_bits=8)
    c_distance  = multiBitFlag(register=_DIST,    lowest_bit=0,num_bits=8)
    c_ichrg     = multiBitFlag(register=_ICHRG,   lowest_bit=0,num_bits=8)

    # Define NVM flags
    f_softboot  = bitFlag(register=_FLAG,bit=0)
    f_solar     = bitFlag(register=_FLAG,bit=1)
    f_burnarm   = bitFlag(register=_FLAG,bit=2)
    f_brownout  = bitFlag(register=_FLAG,bit=3)
    f_triedburn = bitFlag(register=_FLAG,bit=4)
    f_shtdwn    = bitFlag(register=_FLAG,bit=5)
    f_burned    = bitFlag(register=_FLAG,bit=6)
    f_fsk       = bitFlag(register=_FLAG,bit=7)

    def debug_print(self,statement):
        if self.debug:
            print(co("[pysquared]" + str(statement), "red", "bold"))

    def __init__(self):
        """
        Big init routine as the whole board is brought up.
        """
        self.debug=True #Define verbose output here. True or False
        self.BOOTTIME= 1577836800
        self.debug_print(f'Boot time: {self.BOOTTIME}s')
        self.CURRENTTIME=self.BOOTTIME
        self.UPTIME=0
        self.heating=False
        self.is_licensed=False
        self.NORMAL_TEMP=20
        self.NORMAL_BATT_TEMP=1#Set to 0 BEFORE FLIGHT!!!!!
        self.NORMAL_MICRO_TEMP=20
        self.NORMAL_CHARGE_CURRENT=0.5
        self.NORMAL_BATTERY_VOLTAGE=6.9#6.9
        self.CRITICAL_BATTERY_VOLTAGE=6.6#6.6
        self.battery_voltage = 3.3                              # default value for testing REPLACE WITH REAL VALUE
        self.current_draw = 255                                 # default value for testing REPLACE WITH REAL VALUE
        self.data_cache={}
        self.filenumbers={}
        self.image_packets=0
        self.urate = 115200
        self.vlowbatt=6.0
        self.send_buff = memoryview(SEND_BUFF)
        self.micro=microcontroller
        self.radio_cfg = {
                        'id':   0xfb,
                        'gs':   0xfa,
                        'freq': 437.4,
                        'sf':   8,
                        'bw':   125,
                        'cr':   8,
                        'pwr':  23,
                        'st' :  80000
        }
        self.hardware = {
                       'IMU':    False,
                       'Accel':  False,
                       'Radio1': False,
                       'SDcard': False,
                       'LiDAR':  False,
                       'WDT':    False,
                       'SOLAR':  False,
                       'PWR':    False,
                       'FLD':    False,
                       'TEMP':   False,
                       'Face0':  False,
                       'Face1':  False,
                       'Face2':  False,
                       'Face3':  False,
                       'Face4':  False,
                       }

        # Define SPI,I2C,UART | paasing I2C1 to BigData
        try:
            self.i2c0 = busio.I2C(board.I2C0_SCL,board.I2C0_SDA,timeout=5)
            self.spi0 = busio.SPI(board.SPI0_SCK,board.SPI0_MOSI,board.SPI0_MISO)

            self.i2c1 = busio.I2C(board.I2C1_SCL,board.I2C1_SDA,timeout=5,frequency=100000)

            self.uart = busio.UART(board.TX,board.RX,baudrate=self.urate)
        except Exception as e:
            self.debug_print("ERROR INITIALIZING BUSSES: " + ''.join(traceback.format_exception(e)))

        #Define I2C Reset
        self._i2c_reset = digitalio.DigitalInOut(board.I2C_RESET)
        self._i2c_reset.switch_to_output(value=True)

        if self.c_boot > 200:
            self.c_boot=0

        if self.f_fsk:
            self.debug_print("Fsk going to false")
            self.f_fsk=False
        
        if self.f_softboot:
            self.f_softboot=False

        # Initialize IMU
        try:
            self.imu = LSM6DSOX(self.i2c1)
            self.hardware['IMU'] = True
        except Exception as e:
            self.debug_print('[ERROR][IMU]' + ''.join(traceback.format_exception(e)))

        # Initialize Accelerometer
        try:
            self.accelerometer = adafruit_lsm303_accel.LSM303_Accel(self.i2c1)
            self.hardware['Accelerometer'] = True
        except Exception as e:
            self.debug_print('[ERROR][Accelerometer]' + ''.join(traceback.format_exception(e)))


        # Define radio
        _rf_cs1 = digitalio.DigitalInOut(board.SPI0_CS0)
        _rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
        self.enable_rf = digitalio.DigitalInOut(board.RF_ENABLE)
        self.radio1_DIO0=digitalio.DigitalInOut(board.RF1_IO0)
        self.radio1_DIO4=digitalio.DigitalInOut(board.RF1_IO4)

        # self.enable_rf.switch_to_output(value=False) # if U21
        self.enable_rf.switch_to_output(value=True) # if U7
        _rf_cs1.switch_to_output(value=True)
        _rf_rst1.switch_to_output(value=True)
        self.radio1_DIO0.switch_to_input()
        self.radio1_DIO4.switch_to_input()

        # Initialize SD card
        try:
            # Baud rate depends on the card, 4MHz should be safe
            _sd = sdcardio.SDCard(self.spi0, board.SPI0_CS1, baudrate=4000000)
            _vfs = VfsFat(_sd)
            mount(_vfs, "/sd")
            self.fs=_vfs
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
        except Exception as e:
            self.debug_print('[ERROR][SD Card]' + ''.join(traceback.format_exception(e)))

        # Initialize Neopixel
        try:
            self.neopwr = digitalio.DigitalInOut(board.NEO_PWR)
            self.neopwr.switch_to_output(value=True)
            self.neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0,0,255)
            self.hardware['Neopixel'] = True
        except Exception as e:
            self.debug_print('[WARNING][Neopixel]' + ''.join(traceback.format_exception(e)))

        # Initialize radio #1 - UHF
        try:
            self.radio1 = pysquared_rfm9x.RFM9x(self.spi0, _rf_cs1, _rf_rst1,self.radio_cfg['freq'],code_rate=8,baudrate=1320000)
            # Default LoRa Modulation Settings
            # Frequency: 437.4 MHz, SF7, BW125kHz, CR4/8, Preamble=8, CRC=True
            self.radio1.dio0=self.radio1_DIO0
            #self.radio1.dio4=self.radio1_DIO4
            self.radio1.max_output=True
            self.radio1.tx_power=self.radio_cfg['pwr']
            self.radio1.spreading_factor=self.radio_cfg['sf']
            self.radio1.node=self.radio_cfg['id']
            self.radio1.destination=self.radio_cfg['gs']
            self.radio1.enable_crc=True
            self.radio1.ack_delay=0.2
            if self.radio1.spreading_factor > 9: self.radio1.preamble_length = self.radio1.spreading_factor
            self.hardware['Radio1'] = True
            self.enable_rf.value = False
        except Exception as e:
            self.debug_print('[ERROR][RADIO 1]' + ''.join(traceback.format_exception(e)))

        # Prints init state of PySquared hardware
        self.debug_print(str(self.hardware))

        # set power mode
        self.power_mode = 'normal'

    # This fuction might not be needed anymore
    def reinit(self,dev):
        if dev=='pwr':
            self.pwr.__init__(self.i2c0)
        else:
            self.debug_print('Invalid Device? ->' + str(dev))


    '''
    Code to toggle on / off individual faces
    '''
    @property
    def burnarm(self):
        return self.f_burnarm
    @burnarm.setter
    def burnarm(self, value):
        self.f_burnarm = value

    @property
    def burned(self):
        return self.f_burned
    @burned.setter
    def burned(self, value):
        self.f_burned = value

    @property
    def RGB(self):
        return self.neopixel[0]
    @RGB.setter
    def RGB(self,value):
        if self.hardware['Neopixel']:
            try:
                self.neopixel[0] = value
            except Exception as e:
                self.debug_print('[ERROR]' + ''.join(traceback.format_exception(e)))
        else:
            self.debug_print('[WARNING] neopixel not initialized')

    @property
    def uptime(self):
        self.CURRENTTIME=const(time.time())
        return self.CURRENTTIME-self.BOOTTIME

    @property
    def reset_vbus(self):
        # unmount SD card to avoid errors
        if self.hardware['SDcard']:
            try:
                umount('/sd')
                self.spi.deinit()
                time.sleep(3)
            except Exception as e:
                self.debug_print('error unmounting SD card' + ''.join(traceback.format_exception(e)))
        try:
            self._resetReg.drive_mode=digitalio.DriveMode.PUSH_PULL
            self._resetReg.value=1
        except Exception as e:
            self.debug_print('vbus reset error: ' + ''.join(traceback.format_exception(e)))

    @property
    def gyro(self):
        try:
            return self.imu.gyro
        except Exception as e:
            self.debug_print('[ERROR][GYRO]' + ''.join(traceback.format_exception(e)))

    @property
    def imu_accel(self):
        try:
            return self.imu.acceleration
        except Exception as e:
            self.debug_print('[ERROR][ACCEL]' + ''.join(traceback.format_exception(e)))

    @property
    def temp(self):
        try:
            return self.imu.temperature
        except Exception as e:
            self.debug_print('[ERROR][TEMP]' + ''.join(traceback.format_exception(e)))

    @property
    def accel(self):
        try:
            return self.accelerometer.acceleration
        except Exception as e:
            self.debug_print('[ERROR][ACCEL]' + ''.join(traceback.format_exception(e)))

    def log(self,filedir,msg):
        if self.hardware['SDcard']:
            try:
                self.debug_print(f"writing {msg} to {filedir}")
                with open(filedir, "a+") as f:
                    t=int(time.monotonic())
                    f.write('{}, {}\n'.format(t,msg))
            except Exception as e:
                self.debug_print('SD CARD error: ' + ''.join(traceback.format_exception(e)))
        else:
            self.debug_print('[WARNING] SD Card not initialized')
    
    def check_reboot(self):
        self.UPTIME=self.uptime
        self.debug_print(str("Current up time: "+str(self.UPTIME)))
        if self.UPTIME>86400:
            self.reset_vbus()

    def print_file(self,filedir=None,binary=False):
        try:
            if filedir==None:
                raise Exception("file directory is empty")
            self.debug_print(f'--- Printing File: {filedir} ---')
            if binary:
                with open(filedir, "rb") as file:
                    self.debug_print(file.read())
                    self.debug_print('')
            else:
                with open(filedir, "r") as file:
                    for line in file:
                        self.debug_print(line.strip())
        except Exception as e:
            self.debug_print('[ERROR] Cant print file: ' + ''.join(traceback.format_exception(e)))
    
    def read_file(self,filedir=None,binary=False):
        try:
            if filedir==None:
                raise Exception("file directory is empty")
            self.debug_print(f'--- reading File: {filedir} ---')
            if binary:
                with open(filedir, "rb") as file:
                    self.debug_print(file.read())
                    self.debug_print('')
                    return file.read()
            else:
                with open(filedir, "r") as file:
                    for line in file:
                        self.debug_print(line.strip())
                    return file
        except Exception as e:
            self.debug_print('[ERROR] Cant print file: ' + ''.join(traceback.format_exception(e)))

    def powermode(self,mode):
        """
        Configure the hardware for minimum or normal power consumption
        Add custom modes for mission-specific control
        """
        try:
            if 'crit' in mode:
                self.neopixel.brightness=0
                self.enable_rf.value = False
                self.power_mode = 'critical'

            elif 'min' in mode:
                self.neopixel.brightness=0
                self.enable_rf.value = False

                self.power_mode = 'minimum'

            elif 'norm' in mode:
                self.enable_rf.value = True
                self.power_mode = 'normal'
                # don't forget to reconfigure radios, gps, etc...

            elif 'max' in mode:
                self.enable_rf.value = True
                self.power_mode = 'maximum'
        except Exception as e:
            self.debug_print("Error in changing operations of powermode: " + ''.join(traceback.format_exception(e)))


    def new_file(self,substring,binary=False):
        '''
        substring something like '/data/DATA_'
        directory is created on the SD!
        int padded with zeros will be appended to the last found file
        '''
        if self.hardware['SDcard']:
            try:
                ff=''
                n=0
                _folder=substring[:substring.rfind('/')+1]
                _file=substring[substring.rfind('/')+1:]
                self.debug_print('Creating new file in directory: /sd{} with file prefix: {}'.format(_folder,_file))
                try: chdir('/sd'+_folder)
                except OSError:
                    self.debug_print('Directory {} not found. Creating...'.format(_folder))
                    try: mkdir('/sd'+_folder)
                    except Exception as e:
                        self.debug_print("Error with creating new file: " + ''.join(traceback.format_exception(e)))
                        return None
                for i in range(0xFFFF):
                    ff='/sd{}{}{:05}.txt'.format(_folder,_file,(n+i)%0xFFFF)
                    try:
                        if n is not None:
                            stat(ff)
                    except:
                        n=(n+i)%0xFFFF
                        # print('file number is',n)
                        break
                self.debug_print('creating file...'+str(ff))
                if binary: b='ab'
                else: b='a'
                with open(ff,b) as f:
                    f.tell()
                chdir('/')
                return ff
            except Exception as e:
                self.debug_print("Error creating file: " + ''.join(traceback.format_exception(e)))
                return None
        else:
            self.debug_print('[WARNING] SD Card not initialized')



print("Initializing CubeSat")
cubesat = Satellite()
