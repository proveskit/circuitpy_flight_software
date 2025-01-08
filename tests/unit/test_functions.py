import pytest
from FC_Board.lib.pysquared import Satellite
from FC_Board.lib.functions import functions, BatteryHelper, PacketManager, PacketSender

# Remove FC_Board from import w/ new organization of repo


@pytest.fixture  # Setting up mock of cubesat
def mock_cubesat(mocker):
    mock_cubesat = mocker.Mock(spec=Satellite)
    # Creating mock object of Satellite class
    mock_cubesat.debug = True
    mock_cubesat.radio1 = mocker.Mock()  # Creating mock of radio1 attribute
    mock_cubesat.can_bus = mocker.Mock()  # Creating mock of can_bus
    mock_cubesat.watchdog_pet = mocker.Mock()  # Creating mock of watchdog_pet()
    return mock_cubesat  # Returns mock Satellite object


@pytest.fixture  # Initializing functions class with mock cubesat
def funct(mock_cubesat):
    return functions(mock_cubesat)


def test_debug_print_true(funct, mocker):
    # Test debug print when cubesat.debug = True
    mock_print = mocker.patch("builtins.print")  # Mocks built-in print function
    funct.debug_print("Test message")
    mock_print.assert_called_once_with("[Functions]Test message")


def test_debug_print_false(mock_cubesat, mocker):
    # Test debug print when cubesat.debug = False
    mock_cubesat.debug = False
    funct = functions(mock_cubesat)
    # funct object debug state is determined by cubesat debug state
    mock_print = mocker.patch("builtins.print")
    funct.debug_print("Test message")
    mock_print.assert_called_once_with(None)


def test_init(funct, mock_cubesat):
    # Check if cubesat and other attributes are set correctly
    assert funct.cubesat == mock_cubesat
    assert isinstance(funct.battery, BatteryHelper)
    assert funct.battery.cubesat == mock_cubesat
    assert funct.debug == mock_cubesat.debug

    assert isinstance(funct.pm, PacketManager)
    assert isinstance(funct.pm.max_packet_size, int)
    assert funct.pm.max_packet_size == 128  # bytes

    assert isinstance(funct.ps, PacketSender)
    assert funct.ps.radio == mock_cubesat.radio1
    assert funct.ps.pm == funct.pm
    assert isinstance(funct.ps.max_retries, int)
    assert funct.ps.max_retries == 3

    assert isinstance(funct.Errorcount, int)
    assert funct.Errorcount == 0

    assert funct.facestring == [None, None, None, None, None]
    assert isinstance(funct.jokes, list)
    assert all(isinstance(joke, str) for joke in funct.jokes)

    assert isinstance(funct.last_battery_temp, float)
    assert funct.last_battery_temp == 20

    assert isinstance(funct.sleep_duration, int)
    assert funct.sleep_duration == 30  # Should be able to be changed during run time

    assert funct.callsign == "KO6AZM"

    assert isinstance(funct.state_bool, bool)
    assert funct.state_bool == False

    assert isinstance(funct.face_data_baton, bool)
    assert funct.face_data_baton == False

    assert isinstance(funct.detumble_enable_z, bool)
    assert funct.detumble_enable_z == True

    assert isinstance(funct.detumble_enable_x, bool)
    assert funct.detumble_enable_x == True

    assert isinstance(funct.detumble_enable_y, bool)
    assert funct.detumble_enable_y == True


def test_current_check(funct, mock_cubesat):
    # Check if current returned matches that of cubesat current state variable
    current = funct.current_check()
    assert isinstance(current, float)
    assert current == mock_cubesat.current_draw


def test_safe_sleep_short(funct, mock_cubesat, mocker):
    # Mock alarm module functions
    mock_time_alarm = mocker.patch("alarm.time.TimeAlarm")
    mock_light_sleep_until_alarms = mocker.patch("alarm.light_sleep_until_alarms")
    mock_time_monotonic = mocker.patch("time.monotonic", return_value=0)

    # Call safe_sleep for small duration (smaller than 15 sec iteration)
    funct.safe_sleep(10)  # Seconds
    # Check if mock_cubesat.can_bus.sleep() was called
    mock_cubesat.can_bus.sleep.assert_called_once()
    # Check for debug message
    funct.debug_print.assert_called_with("Setting Safe Sleep Mode")

    # Check that alert.time.TimeAlarm was not called
    mock_time_alarm.assert_not_called()
    # Check that alert.light_sleep_until_alarms was not called
    mock_light_sleep_until_alarms.assert_not_called()
    # Check that watchdog_pet() was not called
    mock_cubesat.watchdog_pet.assert_not_called()


# Note: Currently (1/6/25), safe_sleep() can only sleep for as long as 3 minutes (12 iterations of 15 sec = 180 sec)
def test_safe_sleep_long(funct, mock_cubesat, mocker):
    # Mock alarm module functions
    mock_time_alarm = mocker.patch("alarm.time.TimeAlarm")
    mock_light_sleep_until_alarms = mocker.patch("alarm.light_sleep_until_alarms")
    mock_time_monotonic = mocker.patch("time.monotonic", return_value=0)

    # Call safe_sleep for larger duration (larger than 15 sec)
    funct.safe_sleep(45)  # Seconds
    # Check if mock_cubesat.can_bus.sleep() was called
    mock_cubesat.can_bus.sleep.assert_called_once()
    # mock_cubesat.can_bus._set_mode.assert_called_once()

    # Check for debug message
    funct.debug_print.assert_called_with("Setting Safe Sleep Mode")

    # Check that alert.time.TimeAlarm was called 3 times (3 iterations of 15 seconds = 45 sec duration)
    assert mock_time_alarm.call_count == 3
    # Check if alarm.light_sleep_until_alarms was called 3 times
    assert mock_light_sleep_until_alarms.call_count == 3
    # Check if watchdog_pet() was called 3 times
    assert mock_cubesat.watchdog_pet.call_count == 3


def test_listen_loiter(funct, mock_cubesat):
    # Call listen_loiter()
    funct.listen_loiter()
    # Check for debug message
    funct.debug_print.assert_called_with("Listening for 10 seconds")
    # Check if mock_cubesat.radio1 was set to 10
    assert mock_cubesat.radio1.receive_timeout == 10
    # Check if listen() was called
    assert funct.listen.assert_called_once_with(None)
    # Check if safe_sleep() was called with sleep_duration value
    assert funct.safe_sleep.assert_called_once_with(mock_cubesat.sleep_duration)
    # Note: the sleep_duration value that is set to 30, not 20, is passed into safe_sleep
    funct.debug_print.assert_called_with("Sleeping for 20 seconds")
    # Check if watchdog_pet() was called 4 times
    assert mock_cubesat.watchdog_pet.call_count == 4
