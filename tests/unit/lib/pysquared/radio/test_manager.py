from unittest.mock import MagicMock, patch

# from lib.pysquared.rfm9x.manager import RFM9xManager, RFM9xFactory, RFMSPI, RFM9xModulation
import pytest

from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.flag import Flag
from lib.pysquared.rfm9x.modulation import RFM9xModulation
from mocks.circuitpython.byte_array import ByteArray
from stubs.circuitpython.busio import SPI
from stubs.circuitpython.digitalio import DigitalInOut
from stubs.circuitpython.microcontroller import Pin

mock_rfmspi = MagicMock()
mock_rfm9x_module = MagicMock()
mock_rfm9x_module.RFMSPI = mock_rfmspi

with patch.dict(
    "sys.modules",
    {
        "adafruit_rfm": mock_rfm9x_module,
        "adafruit_rfm.rfm_common": mock_rfm9x_module,
        "adafruit_rfm.rfm9xfsk": mock_rfm9x_module,
        "lib.adafruit_rfm.rfm_common": mock_rfm9x_module,
        "lib.adafruit_rfm.rfm9xfsk": mock_rfm9x_module,
    },
):
    from lib.pysquared.rfm9x.manager import RFM9xManager


# @patch('lib.pysquared.rfm9x.manager.RFM9xFactory.create')
@pytest.fixture
def manager() -> RFM9xManager:
    return RFM9xManager(
        Logger(Counter(0, ByteArray(size=8))),
        SPI(Pin()),
        DigitalInOut(Pin()),
        DigitalInOut(Pin()),
        Flag(0, 0, ByteArray(size=8)),
        0,
        1,
        2,
        3,
        4,
    )


def test_set_modulation(manager: RFM9xManager):
    manager.set_modulation(RFM9xModulation.LORA)
    assert manager._use_fsk.get() is False

    manager.set_modulation(RFM9xModulation.FSK)
    assert manager._use_fsk.get() is True


# class TestRFM9xManager(unittest.TestCase):
#     def setUp(self):
#         self.logger = MagicMock()
#         self.spi = MagicMock()
#         self.chip_select = MagicMock()
#         self.reset = MagicMock()
#         self.use_fsk = MagicMock()
#         self.sender_id = 1
#         self.receiver_id = 2
#         self.frequency = 915.0
#         self.transmit_power = 23
#         self.lora_spreading_factor = 7

#         self.manager = RFM9xManager(
#             self.logger,
#             self.spi,
#             self.chip_select,
#             self.reset,
#             self.use_fsk,
#             self.sender_id,
#             self.receiver_id,
#             self.frequency,
#             self.transmit_power,
#             self.lora_spreading_factor,
#         )

#     @patch('lib.pysquared.rfm9x.manager.RFM9xFactory.create')
#     def test_radio_property_creates_radio(self, mock_create):
#         mock_radio = MagicMock(spec=RFMSPI)
#         mock_create.return_value = mock_radio

#         radio = self.manager.radio

#         mock_create.assert_called_once_with(
#             self.logger,
#             self.spi,
#             self.chip_select,
#             self.reset,
#             self.use_fsk,
#             self.sender_id,
#             self.receiver_id,
#             self.frequency,
#             self.transmit_power,
#             self.lora_spreading_factor,
#         )
#         self.assertEqual(radio, mock_radio)
#         self.assertEqual(self.manager._radio, mock_radio)

#     @patch('lib.pysquared.rfm9x.manager.RFM9xFactory.create')
#     def test_radio_property_returns_existing_radio(self, mock_create):
#         mock_radio = MagicMock(spec=RFMSPI)
#         self.manager._radio = mock_radio

#         radio = self.manager.radio

#         mock_create.assert_not_called()
#         self.assertEqual(radio, mock_radio)

#     def test_get_modulation_returns_modulation(self):
#         mock_radio = MagicMock(spec=RFMSPI)
#         mock_radio.get_modulation.return_value = RFM9xModulation.LORA
#         self.manager._radio = mock_radio

#         modulation = self.manager.get_modulation()

#         self.assertEqual(modulation, RFM9xModulation.LORA)
#         mock_radio.get_modulation.assert_called_once()

#     def test_get_modulation_returns_none_if_no_radio(self):
#         self.manager._radio = None

#         modulation = self.manager.get_modulation()

#         self.assertIsNone(modulation)

# if __name__ == '__main__':
#     unittest.main()
