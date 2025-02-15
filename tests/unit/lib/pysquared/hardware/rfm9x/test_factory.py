import math
from unittest.mock import MagicMock, patch

import pytest

from lib.pysquared.hardware.exception import HardwareInitializationError
from lib.pysquared.hardware.rfm9x.factory import RFM9xFactory
from lib.pysquared.hardware.rfm9x.modulation import RFM9xModulation
from mocks.circuitpython.adafruit_rfm.rfm9x import RFM9x
from mocks.circuitpython.adafruit_rfm.rfm9xfsk import RFM9xFSK


@pytest.fixture
def mock_spi():
    return MagicMock()


@pytest.fixture
def mock_chip_select():
    return MagicMock()


@pytest.fixture
def mock_reset():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return MagicMock()


class TestRFM9xFactory:
    def test_create_fsk_radio(self, mock_spi, mock_chip_select, mock_reset):
        frequency = 915
        radio = RFM9xFactory.create_fsk_radio(
            mock_spi, mock_chip_select, mock_reset, frequency
        )
        assert isinstance(radio, RFM9xFSK)
        assert radio.fsk_broadcast_address == 255
        assert radio.fsk_node_address == 1

    def test_create_lora_radio(self, mock_spi, mock_chip_select, mock_reset):
        frequency = 915
        transmit_power = 23
        lora_spreading_factor = 7
        radio = RFM9xFactory.create_lora_radio(
            mock_spi,
            mock_chip_select,
            mock_reset,
            frequency,
            transmit_power,
            lora_spreading_factor,
        )
        assert isinstance(radio, RFM9x)
        assert math.isclose(radio.ack_delay, 0.2)
        assert radio.enable_crc
        assert radio.max_output
        assert radio.spreading_factor == lora_spreading_factor
        assert radio.tx_power == transmit_power

    def test_create_lora_radio_high_sf(self, mock_spi, mock_chip_select, mock_reset):
        frequency = 915
        transmit_power = 23
        lora_spreading_factor = 10
        radio = RFM9xFactory.create_lora_radio(
            mock_spi,
            mock_chip_select,
            mock_reset,
            frequency,
            transmit_power,
            lora_spreading_factor,
        )
        assert isinstance(radio, RFM9x)
        assert radio.preamble_length == lora_spreading_factor

    def test_create_fsk(self, mock_spi, mock_chip_select, mock_reset, mock_logger):
        sender_id = 1
        receiver_id = 2
        frequency = 915
        transmit_power = 23
        lora_spreading_factor = 7

        radio = RFM9xFactory.create(
            mock_logger,
            RFM9xModulation.FSK,
            mock_spi,
            mock_chip_select,
            mock_reset,
            sender_id,
            receiver_id,
            frequency,
            transmit_power,
            lora_spreading_factor,
        )
        assert isinstance(radio, RFM9xFSK)
        assert radio.node == sender_id
        assert radio.destination == receiver_id

    def test_create_lora(self, mock_spi, mock_chip_select, mock_reset, mock_logger):
        sender_id = 1
        receiver_id = 2
        frequency = 915
        transmit_power = 23
        lora_spreading_factor = 7

        radio = RFM9xFactory.create(
            mock_logger,
            RFM9xModulation.LORA,
            mock_spi,
            mock_chip_select,
            mock_reset,
            sender_id,
            receiver_id,
            frequency,
            transmit_power,
            lora_spreading_factor,
        )
        assert isinstance(radio, RFM9x)
        assert radio.node == sender_id
        assert radio.destination == receiver_id

    def test_get_instance_modulation(self):
        mock_fsk_radio = RFM9xFSK(None, None, None, 915)
        mock_lora_radio = RFM9x(None, None, None, 915)

        assert (
            RFM9xFactory.get_instance_modulation(mock_fsk_radio) == RFM9xModulation.FSK
        )
        assert (
            RFM9xFactory.get_instance_modulation(mock_lora_radio)
            == RFM9xModulation.LORA
        )

    def test_create_invalid_modulation(
        self, mock_spi, mock_chip_select, mock_reset, mock_logger
    ):
        sender_id = 1
        receiver_id = 2
        frequency = 915
        transmit_power = 23
        lora_spreading_factor = 7
        radio = RFM9xFactory.create(
            mock_logger,
            "INVALID",
            mock_spi,
            mock_chip_select,
            mock_reset,
            sender_id,
            receiver_id,
            frequency,
            transmit_power,
            lora_spreading_factor,
        )
        assert isinstance(radio, RFM9x)

    @pytest.mark.skip(
        reason="This test is slow because it uses an exponential backoff during retry"
    )
    @patch("lib.pysquared.hardware.rfm9x.factory.RFM9xFactory.create_fsk_radio")
    def test_create_with_retries_fsk(
        self,
        mock_create_fsk_radio,
        mock_spi,
        mock_chip_select,
        mock_reset,
        mock_logger,
    ):
        mock_create_fsk_radio.side_effect = Exception("Simulated FSK failure")

        with pytest.raises(HardwareInitializationError):
            RFM9xFactory.create(
                mock_logger,
                RFM9xModulation.FSK,
                mock_spi,
                mock_chip_select,
                mock_reset,
                1,
                2,
                3,
                4,
                5,
            )
        assert mock_create_fsk_radio.call_count == 3

    @pytest.mark.skip(
        reason="This test is slow because it uses an exponential backoff during retry"
    )
    @patch("lib.pysquared.hardware.rfm9x.factory.RFM9xFactory.create_lora_radio")
    def test_create_with_retries_lora(
        self,
        mock_create_lora_radio,
        mock_spi,
        mock_chip_select,
        mock_reset,
        mock_logger,
    ):
        mock_create_lora_radio.side_effect = Exception("Simulated LoRa failure")

        with pytest.raises(HardwareInitializationError):
            RFM9xFactory.create(
                mock_logger,
                RFM9xModulation.LORA,
                mock_spi,
                mock_chip_select,
                mock_reset,
                1,
                2,
                3,
                4,
                5,
            )
        assert mock_create_lora_radio.call_count == 3
