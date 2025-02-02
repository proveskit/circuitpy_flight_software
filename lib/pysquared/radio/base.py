from typing import Literal, TypeVar

# Type variable for radio subclasses
R = TypeVar('R', bound='Radio')

class Radio:
    @classmethod
    def create(
        cls,
        radio_type: Literal["lora", "fsk"],
        logger,
        sender_id: int,
        receiver_id: int,
        transmit_frequency: int,
        transmit_power: int = None,
        lora_spreading_factor: int = None
    ) -> R:
        """Factory method to create radio instances.
        
        Args:
            radio_type: Type of radio to create ("lora" or "fsk")
            logger: Logger instance
            sender_id: Radio sender ID
            receiver_id: Radio receiver ID 
            transmit_frequency: Radio frequency
            transmit_power: Transmit power (LoRa only)
            lora_spreading_factor: Spreading factor (LoRa only)
        
        Returns:
            Radio instance of specified type
        """
        # Import here to avoid circular imports
        from lib.pysquared.radio.lora import RadioLora
        from lib.pysquared.radio.fsk import RadioFsk

        if radio_type == "lora":
            if transmit_power is None or lora_spreading_factor is None:
                raise ValueError("transmit_power and lora_spreading_factor required for LoRa radio")
            return RadioLora(
                logger=logger,
                sender_id=sender_id,
                receiver_id=receiver_id,
                transmit_frequency=transmit_frequency,
                transmit_power=transmit_power,
                lora_spreading_factor=lora_spreading_factor
            )
        elif radio_type == "fsk":
            return RadioFsk(
                logger=logger,
                sender_id=sender_id,
                receiver_id=receiver_id,
                transmit_frequency=transmit_frequency
            )
        else:
            raise ValueError(f"Unknown radio type: {radio_type}")

    def send_message(self, message: str) -> None:
        raise NotImplementedError("send_message must be implemented by subclasses")

    def receive_message(self) -> str:
        raise NotImplementedError("receive_message must be implemented by subclasses")
