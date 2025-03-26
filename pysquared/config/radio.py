class RadioConfig:
    def __init__(self, radio_dict: dict) -> None:
        self.sender_id: int = radio_dict["sender_id"]
        self.receiver_id: int = radio_dict["receiver_id"]
        self.transmit_frequency: float = radio_dict["transmit_frequency"]
        self.start_time: int = radio_dict["start_time"]
        self.fsk: FSKConfig = FSKConfig(radio_dict["fsk"])
        self.lora: LORAConfig = LORAConfig(radio_dict["lora"])


class FSKConfig:
    def __init__(self, fsk_dict: dict) -> None:
        self.broadcast_address: int = fsk_dict["broadcast_address"]
        self.node_address: int = fsk_dict["node_address"]
        self.modulation_type: int = fsk_dict["modulation_type"]


class LORAConfig:
    def __init__(self, lora_dict: dict) -> None:
        self.ack_delay: float = lora_dict["ack_delay"]
        self.coding_rate: int = lora_dict["coding_rate"]
        self.cyclic_redundancy_check: bool = lora_dict["cyclic_redundancy_check"]
        self.max_output: bool = lora_dict["max_output"]
        self.spreading_factor: int = lora_dict["spreading_factor"]
        self.transmit_power: int = lora_dict["transmit_power"]
