from unittest.mock import MagicMock, patch

import pytest
from digitalio import Direction

from pysquared.hardware.digitalio import initialize_pin
from pysquared.hardware.exception import HardwareInitializationError
from pysquared.logger import Logger


@patch("pysquared.hardware.digitalio.DigitalInOut")
@patch("pysquared.hardware.digitalio.Pin")
def test_initialize_pin_success(mock_pin: MagicMock, mock_digital_in_out: MagicMock):
    # Mock the logger
    mock_logger = MagicMock(spec=Logger)

    # Mock pin and direction
    mock_pin = mock_pin()
    mock_direction = Direction.OUTPUT
    initial_value = True

    # Mock DigitalInOut instance
    mock_dio = mock_digital_in_out.return_value

    # Call fn under test
    _ = initialize_pin(mock_logger, mock_pin, mock_direction, initial_value)

    # Assertions
    mock_digital_in_out.assert_called_once_with(mock_pin)
    assert mock_dio.direction == mock_direction
    assert mock_dio.value == initial_value
    mock_logger.debug.assert_called_once()


@pytest.mark.slow
@patch("pysquared.hardware.digitalio.DigitalInOut")
@patch("pysquared.hardware.digitalio.Pin")
def test_initialize_pin_failure(mock_pin: MagicMock, mock_digital_in_out: MagicMock):
    # Mock the logger
    mock_logger = MagicMock(spec=Logger)

    # Mock pin and direction
    mock_pin = mock_pin()
    mock_direction = Direction.OUTPUT
    initial_value = True

    # Mock DigitalInOut to raise an exception
    mock_digital_in_out.side_effect = Exception("Simulated failure")

    # Call the function and assert exception
    with pytest.raises(HardwareInitializationError):
        initialize_pin(mock_logger, mock_pin, mock_direction, initial_value)

    # Assertions
    assert mock_digital_in_out.call_count == 3  # Called 3 times due to retries
    mock_logger.debug.assert_called()
