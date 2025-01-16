# Written with Claude 3.5
# Nov 10, 2024


class PacketManager:
    def __init__(self, max_packet_size=128):
        """Initialize the packet manager with maximum packet size (default 128 bytes for typical LoRa)"""
        self.max_packet_size = max_packet_size
        self.header_size = 4  # 2 bytes for sequence number, 2 for total packets
        self.payload_size = max_packet_size - self.header_size

    def create_retransmit_request(self, missing_packets):
        """
        Create a packet requesting retransmission
        Format:
        - 2 bytes: 0xFFFF (special sequence number indicating retransmit request)
        - 2 bytes: Number of missing packets
        - Remaining bytes: Missing packet sequence numbers
        """
        header = b"\xff\xff" + len(missing_packets).to_bytes(2, "big")
        payload = b"".join(seq.to_bytes(2, "big") for seq in missing_packets)
        return header + payload

    def is_retransmit_request(self, packet):
        """Check if packet is a retransmit request"""
        return len(packet) >= 4 and packet[:2] == b"\xff\xff"

    def parse_retransmit_request(self, packet):
        """Extract missing packet numbers from retransmit request"""
        num_missing = int.from_bytes(packet[2:4], "big")
        missing = []
        for i in range(num_missing):
            start_idx = 4 + (i * 2)
            seq = int.from_bytes(packet[start_idx : start_idx + 2], "big")
            missing.append(seq)
        return missing

    def pack_data(self, data):
        """
        Takes input data and returns a list of packets ready for transmission
        Each packet includes:
        - 2 bytes: sequence number (0-based)
        - 2 bytes: total number of packets
        - remaining bytes: payload
        """
        # Convert data to bytes if it isn't already
        if not isinstance(data, bytes):
            if isinstance(data, str):
                data = data.encode("utf-8")
            else:
                data = str(data).encode("utf-8")

        # Calculate number of packets needed
        total_packets = (len(data) + self.payload_size - 1) // self.payload_size
        print(f"Packing data of length {len(data)} into {total_packets} packets")

        packets = []
        for seq in range(total_packets):
            # Create header
            header = seq.to_bytes(2, "big") + total_packets.to_bytes(2, "big")
            print(f"Created header: {[hex(b) for b in header]}")

            # Get payload slice for this packet
            start = seq * self.payload_size
            end = start + self.payload_size
            payload = data[start:end]

            # Combine header and payload
            packet = header + payload
            print(
                f"Packet {seq}: length={len(packet)}, header={[hex(b) for b in header]}"
            )
            packets.append(packet)

        return packets

    def unpack_data(self, packets):
        """
        Takes a list of packets and reassembles the original data
        Returns None if packets are missing or corrupted
        """
        if not packets:
            return None

        # Sort packets by sequence number
        try:
            packets = sorted(packets, key=lambda p: int.from_bytes(p[:2], "big"))
        except Exception:
            return None

        # Verify all packets are present
        total_packets = int.from_bytes(packets[0][2:4], "big")
        if len(packets) != total_packets:
            return None

        # Verify sequence numbers are consecutive
        for i, packet in enumerate(packets):
            if int.from_bytes(packet[:2], "big") != i:
                return None

        # Combine payloads
        data = b"".join(packet[self.header_size :] for packet in packets)
        return data

    def create_ack_packet(self, seq_num):
        """Creates an acknowledgment packet for a given sequence number"""
        return b"ACK" + seq_num.to_bytes(2, "big")

    def is_ack_packet(self, packet):
        """Checks if a packet is an acknowledgment packet"""
        return packet.startswith(b"ACK")

    def get_ack_seq_num(self, ack_packet):
        """Extracts sequence number from an acknowledgment packet"""
        if self.is_ack_packet(ack_packet):
            return int.from_bytes(ack_packet[3:5], "big")
        return None
