from unittest.mock import MagicMock

import pytest

from lib.pysquared.hardware.radio.manager import RadioManager
from lib.pysquared.hardware.radio.modulation import RadioModulation
from lib.pysquared.hardware.radio.rfm9x_factory import RFM9xFactory
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.flag import Flag
from mocks.circuitpython.adafruit_rfm.rfm_common import RFMSPI
from mocks.circuitpython.byte_array import ByteArray


@pytest.fixture
def mock_logger():
    return Logger(Counter(0, ByteArray(size=8)))


@pytest.fixture
def mock_use_fsk():
    return Flag(0, 0, ByteArray(size=8))


@pytest.fixture
def mock_radio_factory():
    return MagicMock(spec=RFM9xFactory)


@pytest.mark.parametrize(
    "modulation, use_fsk_initial",
    [(RadioModulation.LORA, False), (RadioModulation.FSK, True)],
)
def test_radio_property_creates_radio(
    mock_logger: Logger,
    mock_radio_factory: MagicMock,
    modulation: RadioModulation,
    use_fsk_initial: bool,
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio_factory.create.return_value = mock_radio

    # Set the flag to use FSK if required
    use_fsk = Flag(0, 0, ByteArray(size=8))
    if use_fsk_initial:
        use_fsk.toggle(True)

    manager = RadioManager(
        mock_logger,
        use_fsk,
        mock_radio_factory,
    )

    radio = manager.radio

    mock_radio_factory.create.assert_called_once_with(
        manager._log,
        modulation,
    )
    assert radio == mock_radio
    assert manager._radio == mock_radio

    # Ensure the next restart is still set to LoRa
    assert manager._use_fsk.get() is False


def test_set_modulation(
    mock_logger: Logger, mock_use_fsk: Flag, mock_radio_factory: MagicMock
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio_factory.create.return_value = mock_radio

    mock_radio.read_u8 = MagicMock()
    manager = RadioManager(
        mock_logger,
        mock_use_fsk,
        mock_radio_factory,
    )

    manager.set_modulation(RadioModulation.LORA)
    assert manager._use_fsk.get() is False

    manager.set_modulation(RadioModulation.FSK)
    assert manager._use_fsk.get() is True

    mock_radio_factory.get_instance_modulation.return_value = RadioModulation.FSK
    manager.set_modulation(RadioModulation.FSK)
    assert manager._use_fsk.get() is True


@pytest.mark.parametrize(
    "raw_value, expected_temperature",
    [
        (0b00110010, 193),  # Example raw value (50)
        (0b10110010, 93),  # Example raw value (178)
    ],
)
def test_get_temperature(
    mock_logger: Logger,
    mock_use_fsk: Flag,
    mock_radio_factory: MagicMock,
    raw_value: int,
    expected_temperature: int,
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio.read_u8 = MagicMock()
    mock_radio.read_u8.return_value = raw_value
    mock_radio_factory.create.return_value = mock_radio

    manager = RadioManager(
        mock_logger,
        mock_use_fsk,
        mock_radio_factory,
    )

    actual_temperature = manager.get_temperature()
    assert actual_temperature == expected_temperature
    mock_radio.read_u8.assert_called_once_with(0x5B)


def test_beacon_radio_message(
    mock_logger: Logger, mock_use_fsk: Flag, mock_radio_factory: MagicMock, capsys
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio.send = MagicMock()
    mock_radio.send.return_value = False
    mock_radio_factory.create.return_value = mock_radio

    manager = RadioManager(mock_logger, mock_use_fsk, mock_radio_factory)

    manager.beacon_radio_message(None)
    assert "There was an error while beaconing" in capsys.readouterr().out

    manager.beacon_radio_message("Testing beaconing function in radio manager.")
    assert "I am beaconing" in capsys.readouterr().out
