class PacketSender:
    def __init__(self, radio, packet_manager, ack_timeout=2.0, max_retries=3, 
                 send_delay=0.2):
        """
        Initialize the packet sender with optimized timing
        """
        self.radio = radio
        self.pm = packet_manager
        self.ack_timeout = ack_timeout
        self.max_retries = max_retries
        self.send_delay = send_delay
        
    def wait_for_ack(self, expected_seq):
        """
        Optimized ACK wait with early return
        """
        import time
        start_time = time.monotonic()
        
        # Minimal delay after sending
        time.sleep(self.send_delay)
        
        while (time.monotonic() - start_time) < self.ack_timeout:
            packet = self.radio.receive()
            
            if packet and self.pm.is_ack_packet(packet):
                ack_seq = self.pm.get_ack_seq_num(packet)
                if ack_seq == expected_seq:
                    # Got our ACK - only wait briefly for a duplicate then continue
                    time.sleep(0.2)
                    return True
            
            time.sleep(0.1)  # Small delay between checks
        
        return False
        
    def send_packet_with_retry(self, packet, seq_num):
        """Optimized packet sending with minimal delays"""
        import time
        
        for attempt in range(self.max_retries):
            self.radio.send(packet)
            
            if self.wait_for_ack(seq_num):
                # Success - minimal delay before next packet
                time.sleep(0.2)
                return True
            
            if attempt < self.max_retries - 1:
                # Only short delay before retry
                time.sleep(1.0)
        
        return False
        
    def send_data(self, data, progress_interval=10):
        """Send data with minimal progress updates"""
        packets = self.pm.pack_data(data)
        total_packets = len(packets)
        print(f"Sending {total_packets} packets...")
        
        for i, packet in enumerate(packets):
            if i % progress_interval == 0:
                print(f"Progress: {i}/{total_packets}")
                
            if not self.send_packet_with_retry(packet, i):
                print(f"Failed at packet {i}/{total_packets}")
                return False
        
        print(f"Successfully sent {total_packets} packets!")
        return True