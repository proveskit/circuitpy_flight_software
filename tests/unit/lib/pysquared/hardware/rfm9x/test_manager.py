from unittest.mock import MagicMock

import pytest

from lib.pysquared.hardware.rfm9x.factory import RFM9xFactory
from lib.pysquared.hardware.rfm9x.manager import RFM9xManager
from lib.pysquared.hardware.rfm9x.modulation import RFM9xModulation
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
    [(RFM9xModulation.LORA, False), (RFM9xModulation.FSK, True)],
)
def test_radio_property_creates_radio(
    mock_logger: Logger,
    mock_radio_factory: MagicMock,
    modulation: RFM9xModulation,
    use_fsk_initial: bool,
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio_factory.create.return_value = mock_radio

    # Set the flag to use FSK if required
    use_fsk = Flag(0, 0, ByteArray(size=8))
    if use_fsk_initial:
        use_fsk.toggle(True)

    manager = RFM9xManager(
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
    manager = RFM9xManager(
        mock_logger,
        mock_use_fsk,
        mock_radio_factory,
    )

    manager.set_modulation(RFM9xModulation.LORA)
    assert manager._use_fsk.get() is False

    manager.set_modulation(RFM9xModulation.FSK)
    assert manager._use_fsk.get() is True

    mock_radio_factory.get_instance_modulation.return_value = RFM9xModulation.FSK
    manager.set_modulation(RFM9xModulation.FSK)
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

    manager = RFM9xManager(
        mock_logger,
        mock_use_fsk,
        mock_radio_factory,
    )

    actual_temperature = manager.get_temperature()
    assert actual_temperature == expected_temperature
    mock_radio.read_u8.assert_called_once_with(0x5B)


async def test_beacon_radio_message(
    mock_logger: Logger, mock_use_fsk: Flag, mock_radio_factory: MagicMock, capsys
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_radio.send = MagicMock()
    mock_radio.send.return_value = False
    mock_radio_factory.create.return_value = mock_radio

    manager = RFM9xManager(mock_logger, mock_use_fsk, mock_radio_factory)

    await manager.beacon_radio_message(None)
    assert "There was an error while beaconing" in capsys.readouterr().out

    await manager.beacon_radio_message("Testing beaconing function in radio manager.")
    assert "I am beaconing" in capsys.readouterr().out
