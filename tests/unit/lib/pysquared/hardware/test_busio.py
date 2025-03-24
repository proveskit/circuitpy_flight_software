from unittest.mock import MagicMock, patch

import pytest
from microcontroller import Pin

from lib.pysquared.hardware.busio import initialize_spi_bus
from lib.pysquared.hardware.exception import HardwareInitializationError
from lib.pysquared.logger import Logger


@patch("lib.pysquared.hardware.busio.SPI")
def test_initialize_spi_bus_success(mock_spi: MagicMock):
    # Mock the logger
    mock_logger = MagicMock(spec=Logger)

    # Mock pins
    mock_clock = MagicMock(spec=Pin)
    mock_mosi = MagicMock(spec=Pin)
    mock_miso = MagicMock(spec=Pin)

    # Mock SPI instance
    mock_spi_instance = mock_spi.return_value

    # Test parameters
    baudrate = 200000
    phase = 1
    polarity = 1
    bits = 16

    # Call fn under test
    result = initialize_spi_bus(
        mock_logger, mock_clock, mock_mosi, mock_miso, baudrate, phase, polarity, bits
    )

    # Assertions
    mock_spi.assert_called_once_with(mock_clock, mock_mosi, mock_miso)
    mock_spi_instance.try_lock.assert_called_once()
    mock_spi_instance.configure.assert_called_once_with(baudrate, phase, polarity, bits)
    mock_spi_instance.unlock.assert_called_once()
    mock_logger.debug.assert_called_once()
    assert result == mock_spi_instance


@pytest.mark.slow
@patch("lib.pysquared.hardware.busio.SPI")
def test_initialize_spi_bus_failure(mock_spi: MagicMock):
    # Mock the logger
    mock_logger = MagicMock(spec=Logger)

    # Mock pins
    mock_clock = MagicMock(spec=Pin)
    mock_mosi = MagicMock(spec=Pin)
    mock_miso = MagicMock(spec=Pin)

    # Mock SPI to raise an exception
    mock_spi.side_effect = Exception("Simulated failure")

    # Call the function and assert exception
    with pytest.raises(HardwareInitializationError):
        initialize_spi_bus(mock_logger, mock_clock, mock_mosi, mock_miso)

    # Assertions
    assert mock_spi.call_count == 3  # Called 3 times due to retries
    mock_logger.debug.assert_called()
