import pytest

from lib.pysquared.functions import Functions
import lib.pysquared.nvm.counter as counter
from lib.pysquared.logger import Logger
from lib.pysquared.config import Config
from lib.pysquared.satellite import Satellite
from lib.pysquared.sleep_helper import SleepHelper
from collections import OrderedDict

# May want to create fake satellites and whatnot to isolate the function library.
@pytest.fixture
def Function():
    count = counter.counter(0, bytearray(8))
    logger = Logger(count)
    config = Config("config.json")
    satellite = Satellite(config, logger, "2.0.0")
    sleep_helper = SleepHelper(satellite, logger)
    return Functions(satellite, logger, config, sleep_helper)

def check_init(function: Functions):
    assert function.satellite is not None
    assert function.logger is not None
    assert function.config is not None
    assert function.sleep_helper is not None
    assert function.cubesat_name == function.config.cubesat_name
    assert function.error_count == 0
    assert function.facestring == [None, None, None, None, None]
    assert function.jokes == function.config.jokes
    assert function.last_battery_temp == function.config.last_battery_temp
    assert function.sleep_duration == function.config.sleep_duration
    assert function.callsign == function.config.callsign
    assert function.state_of_health_part1 is False
    
    assert function.detumble_enable_z == function.config.detumble_enable_z
    assert function.detumble_enable_x == function.config.detumble_enable_x
    assert function.detumble_enable_y == function.config.detumble_enable_y
    
def test_current_draw(function: Functions):
    #test current draw is right format
    current_draw = function.current_draw()
    assert current_draw >= 0
    assert type(current_draw) == float

# just testing that it is correctly called, and foormat is correct
def test_send(capsys, function: Functions):
    #test send is right format
    captured = capsys.readouterr()
    message = "Testy McTestface"
    function.send(message)
    function.cubesat.i
    assert "Sent Packet " + message in captured.out
    

def test_joke(function: Functions):
    #test joke is right format
    joke = function.joke()


def test_format_state_of_health(function: Functions):
    #test  state of health is right format
    hardware_dict = OrderedDict()
    hardware_dict['IMU'] = True
    hardware_dict['GPS'] = True
    hardware_dict['Radio'] = False
    state_of_health = function.format_state_of_health(hardware_dict)
    assert state_of_health == 'IMU=1GPS=1Radio=0'

