import sys
import os
import pytest


# To prevent ModuleNotFound of lib: Add the root directory of your project to the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# This configuration file can automatically be seen and used by all pytests
# Mocking any necessary hardware with pytest-mock mocker
@pytest.fixture
def mock_hardware_modules(mocker):
    mocker.patch.dict(
        "sys.modules",
        {
            "board": mocker.Mock(),
            "machine": mocker.Mock(),
            "microcontroller": mocker.Mock(),
            "alarm": mocker.Mock(),
            # Include hardware mocks as needed (ex. 'machine': mocker.Mock(), 'microcontroller': mocker.Mock() ...)
        },
    )


@pytest.fixture  # Setting up mock of cubesat
def mock_cubesat(mocker):
    from lib.pysquared.pysquared import Satellite

    mock_cubesat = mocker.Mock(
        spec=Satellite
    )  # Creating mock object of Satellite class
    mock_cubesat.debug = True
    # Creating any necessary mocks of attributes within Satellite class mock
    mock_cubesat.radio1 = mocker.Mock()  # Creating mock of radio1 attribute
    mock_cubesat.can_bus = mocker.Mock()  # Creating mock of can_bus
    mock_cubesat.watchdog_pet = mocker.Mock()  # Creating mock of watchdog_pet()
    return mock_cubesat  # Returns mock Satellite object


@pytest.fixture  # Initializing functions class with mock cubesat
def funct(mock_cubesat):
    from lib.pysquared.functions import functions

    return functions(mock_cubesat)
