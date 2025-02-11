from unittest.mock import MagicMock

import pytest

from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.flag import Flag
from lib.pysquared.rfm9x.factory import RFM9xFactory
from lib.pysquared.rfm9x.manager import RFM9xManager
from lib.pysquared.rfm9x.modulation import RFM9xModulation
from mocks.circuitpython.adafruit_rfm.rfm_common import RFMSPI
from mocks.circuitpython.byte_array import ByteArray
from stubs.circuitpython.busio import SPI
from stubs.circuitpython.digitalio import DigitalInOut
from stubs.circuitpython.microcontroller import Pin


@pytest.fixture
def mock_rfm9x_factory(monkeypatch):
    mock_factory = MagicMock(spec=RFM9xFactory)
    monkeypatch.setattr("lib.pysquared.rfm9x.manager.RFM9xFactory", mock_factory)
    return mock_factory


@pytest.mark.parametrize(
    "modulation, use_fsk_initial",
    [(RFM9xModulation.LORA, False), (RFM9xModulation.FSK, True)],
)
def test_radio_property_creates_radio(
    mock_rfm9x_factory: MagicMock,
    modulation: RFM9xModulation,
    use_fsk_initial: bool,
):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_rfm9x_factory.create.return_value = mock_radio

    # Set the flag to use FSK if required
    use_fsk = Flag(0, 0, ByteArray(size=8))
    if use_fsk_initial:
        use_fsk.toggle(True)

    manager = RFM9xManager(
        Logger(Counter(0, ByteArray(size=8))),
        use_fsk,
        mock_rfm9x_factory,
        SPI(Pin()),
        DigitalInOut(Pin()),
        DigitalInOut(Pin()),
        0,
        1,
        2,
        3,
        4,
    )

    radio = manager.radio

    mock_rfm9x_factory.create.assert_called_once_with(
        manager._log,
        modulation,
        manager._spi,
        manager._chip_select,
        manager._reset,
        manager._sender_id,
        manager._receiver_id,
        manager._frequency,
        manager._transmit_power,
        manager._lora_spreading_factor,
    )
    assert radio == mock_radio
    assert manager._radio == mock_radio

    # Ensure the next restart is still set to LoRa
    assert manager._use_fsk.get() is False


def test_set_modulation(mock_rfm9x_factory: MagicMock):
    mock_radio = MagicMock(spec=RFMSPI)
    mock_rfm9x_factory.create.return_value = mock_radio

    manager = RFM9xManager(
        Logger(Counter(0, ByteArray(size=8))),
        Flag(0, 0, ByteArray(size=8)),
        mock_rfm9x_factory,
        SPI(Pin()),
        DigitalInOut(Pin()),
        DigitalInOut(Pin()),
        0,
        1,
        2,
        3,
        4,
    )

    manager.set_modulation(RFM9xModulation.LORA)
    assert manager._use_fsk.get() is False

    manager.set_modulation(RFM9xModulation.FSK)
    assert manager._use_fsk.get() is True

    mock_rfm9x_factory.get_instance_modulation.return_value = RFM9xModulation.FSK
    manager.set_modulation(RFM9xModulation.FSK)
    assert manager._use_fsk.get() is True
