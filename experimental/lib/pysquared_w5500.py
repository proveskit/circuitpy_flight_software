# SPDX-FileCopyrightText: 2010 WIZnet
# SPDX-FileCopyrightText: 2010 Arduino LLC
# SPDX-FileCopyrightText: 2008 Bjoern Hartmann
# SPDX-FileCopyrightText: 2018 Paul Stoffregen
# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Patrick Van Oosterwijck
# SPDX-FileCopyrightText: 2021 Adam Cummick
# SPDX-FileCopyrightText: 2023 Martin Stephens
# SPDX-FileCopyrightText: 2023 Nicole Maggard
# SPDX-License-Identifier: MIT
"""
`adafruit_wiznet5k`
================================================================================
* Author(s): WIZnet, Arduino LLC, Bjoern Hartmann, Paul Stoffregen, Brent Rubell,
  Patrick Van Oosterwijck, Martin Stephens, Nicole Maggard
"""

from __future__ import annotations

try:
    from typing import TYPE_CHECKING, Optional, Union, List, Tuple

    if TYPE_CHECKING:
        from circuitpython_typing import WriteableBuffer
        import busio
        import digitalio

        IpAddress4Raw = Union[bytes, Tuple[int, int, int, int]]
        MacAddressRaw = Union[bytes, Tuple[int, int, int, int, int, int]]
except ImportError:
    pass

from random import randint
import time
import gc
from sys import byteorder
from micropython import const
from debugcolor import co

from adafruit_bus_device.spi_device import SPIDevice

# *** Wiznet Common Registers ***
_REG_MR = const(0x0000)
# Gateway IPv4 Address.
_REG_GAR = const(0x0001)
# Subnet Mask Address
_REG_SUBR = const(0x0005)
# Chip version.
_REG_VERSIONR = const(0x0039)
# Source Hardware Address
_REG_SHAR = const(0x0009)
# Source IP Address
_REG_SIPR = const(0x000F)
# Register with link status flag (PHYCFGR for 5xxxx, PHYSR for 6100).
_REG_LINK_FLAG = const(0x002E)
_REG_RCR = const(0x001B)
_REG_RTR = const(0x0019)

# *** Wiznet Socket Registers ***
# Socket n Mode.
_REG_SNMR = const(0x0000)
# Socket n Command.
_REG_SNCR = const(0x0001)
# Socket n Interrupt.
_REG_SNIR = const(0x0002)
# Socket n Status.
_REG_SNSR = const(0x0003)
# Socket n Source Port.
_REG_SNPORT = const(0x0004)
# Destination IPv4 Address.
_REG_SNDIPR = const(0x000C)
# Destination Port.
_REG_SNDPORT = const(0x0010)
# RX Free Size.
_REG_SNRX_RSR = const(0x0026)
# Read Size Pointer.
_REG_SNRX_RD = const(0x0028)
# Socket n TX Free Size.
_REG_SNTX_FSR = const(0x0020)
# TX Write Pointer.
_REG_SNTX_WR = const(0x0024)
# SNSR Commands
SNSR_SOCK_CLOSED = const(0x00)
_SNSR_SOCK_INIT = const(0x13)
SNSR_SOCK_LISTEN = const(0x14)
_SNSR_SOCK_SYNSENT = const(0x15)
SNSR_SOCK_SYNRECV = const(0x16)
SNSR_SOCK_ESTABLISHED = const(0x17)
SNSR_SOCK_FIN_WAIT = const(0x18)
_SNSR_SOCK_CLOSING = const(0x1A)
SNSR_SOCK_TIME_WAIT = const(0x1B)
SNSR_SOCK_CLOSE_WAIT = const(0x1C)
_SNSR_SOCK_LAST_ACK = const(0x1D)
_SNSR_SOCK_UDP = const(0x22)
_SNSR_SOCK_IPRAW = const(0x32)
_SNSR_SOCK_MACRAW = const(0x42)
_SNSR_SOCK_PPPOE = const(0x5F)

# Sock Commands (CMD)
_CMD_SOCK_OPEN = const(0x01)
_CMD_SOCK_LISTEN = const(0x02)
_CMD_SOCK_CONNECT = const(0x04)
_CMD_SOCK_DISCON = const(0x08)
_CMD_SOCK_CLOSE = const(0x10)
_CMD_SOCK_SEND = const(0x20)
_CMD_SOCK_SEND_MAC = const(0x21)
_CMD_SOCK_SEND_KEEP = const(0x22)
_CMD_SOCK_RECV = const(0x40)

# Socket n Interrupt Register
_SNIR_SEND_OK = const(0x10)
SNIR_TIMEOUT = const(0x08)
_SNIR_RECV = const(0x04)
SNIR_DISCON = const(0x02)
_SNIR_CON = const(0x01)

_CH_SIZE = const(0x100)
_SOCK_SIZE = const(0x800)  # MAX W5k socket size
_SOCK_MASK = const(0x7FF)
# Register commands
_MR_RST = const(0x80)  # Mode Register RST
# Socket mode register
_SNMR_CLOSE = const(0x00)
_SNMR_TCP = const(0x21)
SNMR_UDP = const(0x02)
_SNMR_IPRAW = const(0x03)
_SNMR_MACRAW = const(0x04)
_SNMR_PPPOE = const(0x05)

_MAX_PACKET = const(4000)
_LOCAL_PORT = const(0x400)
# Default hardware MAC address
_DEFAULT_MAC = (0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED)

# Maximum number of sockets to support, differs between chip versions.
_MAX_SOCK_NUM = const(0x08)
_SOCKET_INVALID = const(0xFF)


def _unprettyfy(data: str, seperator: str, correct_length: int) -> bytes:
    """Helper for converting . or : delimited strings to bytes objects."""
    data = bytes(int(x) for x in data.split(seperator))
    if len(data) == correct_length:
        return data
    raise ValueError("Invalid IP or MAC address.")


class WIZNET5500:
    """Interface for WIZNET5K module."""

    _TCP_MODE = const(0x21)
    _UDP_MODE = const(0x02)

    _sockets_reserved = []
    def debug_print(self,statement:str = '') -> None:
        """
        :param statement: message to get printed in debug print
        """
        if self._debug:
            print(co("[W5500]" + str(statement), 'blue', 'bold'))

    def __init__(
        self,
        spi_bus: busio.SPI,
        cs: digitalio.DigitalInOut,  # pylint: disable=invalid-name
        reset: Optional[digitalio.DigitalInOut] = None,
        mac: Union[MacAddressRaw, str] = _DEFAULT_MAC,
        hostname: Optional[str] = None,
        debug: bool = False,
    ) -> None:
        """
        :param busio.SPI spi_bus: The SPI bus the Wiznet module is connected to.
        :param digitalio.DigitalInOut cs: Chip select pin.
        :param digitalio.DigitalInOut reset: Optional reset pin, defaults to None.
        :param Union[MacAddressRaw, str] mac: The Wiznet's MAC Address, defaults to
            (0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED).
        :param str hostname: The desired hostname, with optional {} to fill in the MAC
            address, defaults to None.
        :param bool debug: Enable debugging output, defaults to False.
        """
        self._debug = debug
        self._chip_type = None
        self._device = SPIDevice(spi_bus, cs, baudrate=8000000, polarity=0, phase=0)
        # init c.s.
        self._cs = cs

        # Reset wiznet module prior to initialization.
        if reset:
            reset.value = False
            time.sleep(0.1)
            reset.value = True
            time.sleep(0.1)

        # Setup chip_select pin.
        time.sleep(1)
        self._cs.switch_to_output()
        self._cs.value = 1

        # Buffer for reading params from module
        self._pbuff = bytearray(8)
        self._rxbuf = bytearray(_MAX_PACKET)

        # attempt to initialize the module
        self._ch_base_msb = 0
        self._src_ports_in_use = []
        self._wiznet_chip_init()

        # Set MAC address
        self.mac_address = mac
        self.src_port = 0
        # udp related
        self.udp_from_ip = [b"\x00\x00\x00\x00"] * self.max_sockets
        self.udp_from_port = [0] * self.max_sockets

        # Wait to give the Ethernet link to initialise.
        stop_time = time.monotonic() + 5
        while time.monotonic() < stop_time:
            if self.link_status:
                break
            self.debug_print("Ethernet link is down…")
            time.sleep(0.5)

    @property
    def max_sockets(self) -> int:
        """
        Maximum number of sockets supported by chip.

        :return int: Maximum supported sockets.
        """
        return _MAX_SOCK_NUM

    @property
    def chip(self) -> str:
        """
        Ethernet controller chip type.

        :return str: The chip type.
        """
        return self._chip_type

    @property
    def ip_address(self) -> bytes:
        """
        Configured IP address for the WIZnet Ethernet hardware.

        :return bytes: IP address as four bytes.
        """
        return self._read(_REG_SIPR, 0x00, 4)

    @staticmethod
    def pretty_ip(ipv4: bytes) -> str:
        """
        Convert a 4 byte IP address to a dotted-quad string for printing.

        :param bytearray ipv4: A four byte IP address.

        :return str: The IP address (a string of the form '255.255.255.255').

        :raises ValueError: If IP address is not 4 bytes.
        """
        if len(ipv4) != 4:
            raise ValueError("Wrong length for IPv4 address.")
        return ".".join(f"{byte}" for byte in ipv4)

    @staticmethod
    def unpretty_ip(ipv4: str) -> bytes:
        """
        Convert a dotted-quad string to a four byte IP address.

        :param str ipv4: IPv4 address (a string of the form '255.255.255.255') to be converted.

        :return bytes: IPv4 address in four bytes.

        :raises ValueError: If IPv4 address is not 4 bytes.
        """
        return _unprettyfy(ipv4, ".", 4)

    @property
    def mac_address(self) -> bytes:
        """
        The WIZnet Ethernet hardware MAC address.

        :return bytes: Six byte MAC address.
        """
        return self._read(_REG_SHAR, 0x00, 6)

    @mac_address.setter
    def mac_address(self, address: Union[MacAddressRaw, str]) -> None:
        """
        Set the WIZnet hardware MAC address.

        :param Union[MacAddressRaw, str] address: A hardware MAC address.

        :raises ValueError: If the MAC address is invalid
        """
        try:
            address = [int(x, 16) for x in address.split(":")]
        except AttributeError:
            pass
        try:
            if len(address) != 6:
                raise ValueError()
            # Bytes conversion will raise ValueError if values are not 0-255
            self._write(_REG_SHAR, 0x04, bytes(address))
        except ValueError:
            # pylint: disable=raise-missing-from
            raise ValueError("Invalid MAC address.")

    @staticmethod
    def pretty_mac(mac: bytes) -> str:
        """
        Convert a bytes MAC address to a ':' seperated string for display.

        :param bytes mac: The MAC address.

        :return str: Mac Address in the form 00:00:00:00:00:00

        :raises ValueError: If MAC address is not 6 bytes.
        """
        if len(mac) != 6:
            raise ValueError("Incorrect length for MAC address.")
        return ":".join(f"{byte:02x}" for byte in mac)

    def remote_ip(self, socket_num: int) -> str:
        """
        IP address of the host which sent the current incoming packet.

        :param int socket_num: ID number of the socket to check.

        :return str: The IPv4 address.

        :raises ValueError: If the socket number is out of range.
        """
        self._sock_num_in_range(socket_num)
        for octet in range(4):
            self._pbuff[octet] = self._read_socket_register(
                socket_num, _REG_SNDIPR + octet
            )
        return self.pretty_ip(self._pbuff[:4])

    def remote_port(self, socket_num: int) -> int:
        """
        Port number of the host which sent the current incoming packet.

        :param int socket_num: ID number of the socket to check.

        :return int: The incoming port number of the socket connection.

        :raises ValueError: If the socket number is out of range.
        """
        self._sock_num_in_range(socket_num)
        return self._read_two_byte_sock_reg(socket_num, _REG_SNDPORT)

    @property
    def link_status(self) -> bool:
        """
        Physical hardware (PHY) connection status.

        Whether the WIZnet hardware is physically connected to an Ethernet network.

        :return bool: True if the link is up, False if the link is down.
        """
        return bool(
            int.from_bytes(self._read(_REG_LINK_FLAG, 0x00), "big")
            & 0x01
        )

    @property
    def ifconfig(self) -> Tuple[bytes, bytes, bytes, bytes]:
        """
        Network configuration information.

        :return Tuple[bytes, bytes, bytes, bytes]: The IP address, subnet mask, gateway
            address and DNS server address.
        """
        return (
            self.ip_address,
            self._read(_REG_SUBR, 0x00, 4),
            self._read(_REG_GAR, 0x00, 4),
            self._dns,
        )

    @ifconfig.setter
    def ifconfig(
        self, params: Tuple[IpAddress4Raw, IpAddress4Raw, IpAddress4Raw, IpAddress4Raw]
    ) -> None:
        """
        Set network configuration.

        :param Tuple[Address4Bytes, Address4Bytes, Address4Bytes, Address4Bytes]: Configuration
            settings - (ip_address, subnet_mask, gateway_address, dns_server).
        """
        for param in params:
            if len(param) != 4:
                raise ValueError("IPv4 address must be 4 bytes.")
        ip_address, subnet_mask, gateway_address, dns_server = params

        self._write(_REG_SIPR, 0x04, bytes(ip_address))
        self._write(_REG_SUBR, 0x04, bytes(subnet_mask))
        self._write(_REG_GAR, 0x04, bytes(gateway_address))

        self._dns = bytes(dns_server)

    # *** Public Socket Methods ***

    def socket_available(self, socket_num: int, sock_type: int = _SNMR_TCP) -> int:
        """
        Number of bytes available to be read from the socket.

        :param int socket_num: Socket to check for available bytes.
        :param int sock_type: Socket type. Use SNMR_TCP for TCP or SNMR_UDP for UDP,
            defaults to SNMR_TCP.

        :return int: Number of bytes available to read.

        :raises ValueError: If the socket number is out of range.
        :raises ValueError: If the number of bytes on a UDP socket is negative.
        """
        self.debug_print(f"socket_available called on socket {socket_num}, protocol {sock_type}")
        self._sock_num_in_range(socket_num)

        number_of_bytes = self._get_rx_rcv_size(socket_num)
        if self._read_snsr(socket_num) == SNMR_UDP:
            number_of_bytes -= 8  # Subtract UDP header from packet size.
        if number_of_bytes < 0:
            raise ValueError("Negative number of bytes found on socket.")
        return number_of_bytes

    def socket_status(self, socket_num: int) -> int:
        """
        Socket connection status.

        Can be: SNSR_SOCK_CLOSED, SNSR_SOCK_INIT, SNSR_SOCK_LISTEN, SNSR_SOCK_SYNSENT,
        SNSR_SOCK_SYNRECV, SNSR_SYN_SOCK_ESTABLISHED, SNSR_SOCK_FIN_WAIT,
        SNSR_SOCK_CLOSING, SNSR_SOCK_TIME_WAIT, SNSR_SOCK_CLOSE_WAIT, SNSR_LAST_ACK,
        SNSR_SOCK_UDP, SNSR_SOCK_IPRAW, SNSR_SOCK_MACRAW, SNSR_SOCK_PPOE.

        :param int socket_num: ID of socket to check.

        :return int: The connection status.
        """
        return self._read_snsr(socket_num)

    def socket_connect(
        self,
        socket_num: int,
        dest: IpAddress4Raw,
        port: int,
        conn_mode: int = _SNMR_TCP,
    ) -> int:
        """
        Open and verify a connection from a socket to a destination IPv4 address
        or hostname. A TCP connection is made by default. A UDP connection can also
        be made.

        :param int socket_num: ID of the socket to be connected.
        :param IpAddress4Raw dest: The destination as a host name or IP address.
        :param int port: Port to connect to (0 - 65,535).
        :param int conn_mode: The connection mode. Use SNMR_TCP for TCP or SNMR_UDP for UDP,
            defaults to SNMR_TCP.

        :raises ValueError: if the socket number is out of range.
        :raises ConnectionError: If the connection to the socket cannot be established.
        """
        self._sock_num_in_range(socket_num)
        self._check_link_status()
        self.debug_print(f"W5500 socket connect, protocol={conn_mode}, port={port}, ip={self.pretty_ip(dest)}")
        # initialize a socket and set the mode
        self.socket_open(socket_num, conn_mode=conn_mode)
        # set socket destination IP and port
        self._write_sndipr(socket_num, dest)
        self._write_sndport(socket_num, port)
        self._write_sncr(socket_num, _CMD_SOCK_CONNECT)
        if conn_mode == _SNMR_TCP:
            # wait for tcp connection establishment
            while self.socket_status(socket_num) != SNSR_SOCK_ESTABLISHED:
                time.sleep(0.001)
                self.debug_print(f"SNSR: {self.socket_status(socket_num)}")
                if self.socket_status(socket_num) == SNSR_SOCK_CLOSED:
                    raise ConnectionError("Failed to establish connection.")
        return 1

    def get_socket(self, *, reserve_socket=False) -> int:
        """
        Request, allocate and return a socket from the WIZnet 5k chip.

        Cycle through the sockets to find the first available one. If the called with
        reserve_socket=True, update the list of reserved sockets (intended to be used with
        socket.socket()). Note that reserved sockets must be released by calling
        release_socket() once they are no longer needed.

        If all sockets are reserved, no sockets are available for DNS calls, etc. Therefore,
        one socket cannot be reserved. Since socket 0 is the only socket that is capable of
        operating in MacRAW mode, it is the non-reservable socket.

        :param bool reserve_socket: Whether to reserve the socket.

        :returns int: The first available socket.

        :raises RuntimeError: If no socket is available.
        """
        self.debug_print("*** Get socket.")
        # Prefer socket zero for none reserved calls as it cannot be reserved.
        if not reserve_socket and self.socket_status(0) == SNSR_SOCK_CLOSED:
            self.debug_print("Allocated socket # 0")
            return 0
        # Then check the other sockets.

        #  Call garbage collection to encourage socket.__del__() be called to on any
        #  destroyed instances. Not at all guaranteed to work!
        gc.collect()
        self.debug_print(f"Reserved sockets: {WIZNET5500._sockets_reserved}")

        for socket_number, reserved in enumerate(WIZNET5500._sockets_reserved, start=1):
            if not reserved and self.socket_status(socket_number) == SNSR_SOCK_CLOSED:
                if reserve_socket:
                    WIZNET5500._sockets_reserved[socket_number - 1] = True
                    self.debug_print(f"Allocated socket # {socket_number}.")
                return socket_number
        raise RuntimeError("All sockets in use.")

    def release_socket(self, socket_number):
        """
        Update the socket reservation list when a socket is no longer reserved.

        :param int socket_number: The socket to release.

        :raises ValueError: If the socket number is out of range.
        """
        self._sock_num_in_range(socket_number)
        WIZNET5500._sockets_reserved[socket_number - 1] = False

    def socket_listen(
        self, socket_num: int, port: int, conn_mode: int = _SNMR_TCP
    ) -> None:
        """
        Listen on a socket's port.

        :param int socket_num: ID of socket to listen on.
        :param int port: Port to listen on (0 - 65,535).
        :param int conn_mode: Connection mode SNMR_TCP for TCP or SNMR_UDP for
            UDP, defaults to SNMR_TCP.

        :raises ValueError: If the socket number is out of range.
        :raises ConnectionError: If the Ethernet link is down.
        :raises RuntimeError: If unable to connect to a hardware socket.
        """
        self._sock_num_in_range(socket_num)
        self._check_link_status()
        self.debug_print(f"* Listening on port={port}, ip={self.pretty_ip(self.ip_address)}")
        # Initialize a socket and set the mode
        self.src_port = port
        self.socket_open(socket_num, conn_mode=conn_mode)
        self.src_port = 0
        # Send listen command
        self._write_sncr(socket_num, _CMD_SOCK_LISTEN)
        # Wait until ready
        status = SNSR_SOCK_CLOSED
        while status not in (
            SNSR_SOCK_LISTEN,
            SNSR_SOCK_ESTABLISHED,
            _SNSR_SOCK_UDP,
        ):
            status = self._read_snsr(socket_num)
            if status == SNSR_SOCK_CLOSED:
                raise RuntimeError("Listening socket closed.")

    def socket_accept(self, socket_num: int) -> Tuple[int, Tuple[str, int]]:
        """
        Destination IPv4 address and port from an incoming connection.

        Return the next socket number so listening can continue, along with
        the IP address and port of the incoming connection.

        :param int socket_num: Socket number with connection to check.

        :return Tuple[int, Tuple[Union[str, bytearray], Union[int, bytearray]]]:
            If successful, the next (socket number, (destination IP address, destination port)).

        :raises ValueError: If the socket number is out of range.
        """
        self._sock_num_in_range(socket_num)
        dest_ip = self.remote_ip(socket_num)
        dest_port = self.remote_port(socket_num)
        next_socknum = self.get_socket()
        self.debug_print(f"Dest is ({dest_ip}, {dest_port}), Next listen socknum is #{next_socknum}")
        return next_socknum, (dest_ip, dest_port)

    def socket_open(self, socket_num: int, conn_mode: int = _SNMR_TCP) -> None:
        """
        Open an IP socket.

        The socket may connect via TCP or UDP protocols.

        :param int socket_num: The socket number to open.
        :param int conn_mode: The protocol to use. Use SNMR_TCP for TCP or SNMR_UDP for \
            UDP, defaults to SNMR_TCP.

        :raises ValueError: If the socket number is out of range.
        :raises ConnectionError: If the Ethernet link is down or no connection to socket.
        :raises RuntimeError: If unable to open a socket in UDP or TCP mode.
        """
        self._sock_num_in_range(socket_num)
        self._check_link_status()
        self.debug_print(f"*** Opening socket {socket_num}")
        if self._read_snsr(socket_num) not in (
            SNSR_SOCK_CLOSED,
            SNSR_SOCK_TIME_WAIT,
            SNSR_SOCK_FIN_WAIT,
            SNSR_SOCK_CLOSE_WAIT,
            _SNSR_SOCK_CLOSING,
            _SNSR_SOCK_UDP,
        ):
            raise ConnectionError("Failed to initialize a connection with the socket.")
        self.debug_print(f"* Opening W5500 Socket, protocol={conn_mode}")
        time.sleep(0.00025)

        self._write_snmr(socket_num, conn_mode)
        self.write_snir(socket_num, 0xFF)

        if self.src_port > 0:
            # write to socket source port
            self._write_sock_port(socket_num, self.src_port)
        else:
            s_port = randint(49152, 65535)
            while s_port in self._src_ports_in_use:
                s_port = randint(49152, 65535)
            self._write_sock_port(socket_num, s_port)
            self._src_ports_in_use[socket_num] = s_port

        # open socket
        self._write_sncr(socket_num, _CMD_SOCK_OPEN)
        if self._read_snsr(socket_num) not in [_SNSR_SOCK_INIT, _SNSR_SOCK_UDP]:
            raise RuntimeError("Could not open socket in TCP or UDP mode.")

    def socket_close(self, socket_num: int) -> None:
        """
        Close a socket.

        :param int socket_num: The socket to close.

        :raises ValueError: If the socket number is out of range.
        """
        self.debug_print(f"*** Closing socket {socket_num}")
        self._sock_num_in_range(socket_num)
        self._write_sncr(socket_num, _CMD_SOCK_CLOSE)
        self.debug_print("  Waiting for socket to close…")
        timeout = time.monotonic() + 5.0
        while self._read_snsr(socket_num) != SNSR_SOCK_CLOSED:
            if time.monotonic() > timeout:
                raise RuntimeError("W5500 failed to close socket, status = {}.".format(self._read_snsr(socket_num)))
            time.sleep(0.0001)
        self.debug_print("  Socket has closed.")

    def socket_disconnect(self, socket_num: int) -> None:
        """
        Disconnect a TCP or UDP connection.

        :param int socket_num: The socket to close.

        :raises ValueError: If the socket number is out of range.
        """
        self.debug_print(f"*** Disconnecting socket {socket_num}")
        self._sock_num_in_range(socket_num)
        self._write_sncr(socket_num, _CMD_SOCK_DISCON)

    def socket_read(self, socket_num: int, length: int) -> Tuple[int, bytes]:
        """
        Read data from a hardware socket. Called directly by TCP socket objects and via
        read_udp() for UDP socket objects.

        :param int socket_num: The socket to read data from.
        :param int length: The number of bytes to read from the socket.

        :returns Tuple[int, bytes]: If the read was successful then the first
            item of the tuple is the length of the data and the second is the data.
            If the read was unsuccessful then 0, b"" is returned.

        :raises ValueError: If the socket number is out of range.
        :raises ConnectionError: If the Ethernet link is down.
        :raises RuntimeError: If the socket connection has been lost.
        """
        self._sock_num_in_range(socket_num)
        self._check_link_status()

        # Check if there is data available on the socket
        bytes_on_socket = self._get_rx_rcv_size(socket_num)
        self.debug_print(f"Bytes avail. on sock: {bytes_on_socket}")
        if bytes_on_socket:
            bytes_on_socket = length if bytes_on_socket > length else bytes_on_socket
            self.debug_print(f"* Processing {bytes_on_socket} bytes of data")
            # Read the starting save address of the received data.
            pointer = self._read_snrx_rd(socket_num)
            # Read data from the hardware socket.
            bytes_read = self._chip_socket_read(socket_num, pointer, bytes_on_socket)
            # After reading the received data, update Sn_RX_RD register.
            pointer = (pointer + bytes_on_socket) & 0xFFFF
            self._write_snrx_rd(socket_num, pointer)
            self._write_sncr(socket_num, _CMD_SOCK_RECV)
        else:
            # no data on socket
            if self._read_snmr(socket_num) in (
                SNSR_SOCK_LISTEN,
                SNSR_SOCK_CLOSED,
                SNSR_SOCK_CLOSE_WAIT,
            ):
                raise RuntimeError("Lost connection to peer.")
            bytes_read = b""
        return bytes_on_socket, bytes_read

    def read_udp(self, socket_num: int, length: int) -> Tuple[int, bytes]:
        """
        Read UDP socket's current message bytes.

        :param int socket_num: The socket to read data from.
        :param int length: The number of bytes to read from the socket.

        :return Tuple[int, bytes]: If the read was successful then the first
            item of the tuple is the length of the data and the second is the data.
            If the read was unsuccessful then (0, b"") is returned.

        :raises ValueError: If the socket number is out of range.
        """
        self._sock_num_in_range(socket_num)
        bytes_on_socket, bytes_read = 0, b""
        # Parse the UDP packet header.
        header_length, self._pbuff[:8] = self.socket_read(socket_num, 8)
        if header_length:
            if header_length != 8:
                raise ValueError("Invalid UDP header.")
            data_length = self._chip_parse_udp_header(socket_num)
            # Read the UDP packet data.
            if data_length:
                if data_length <= length:
                    bytes_on_socket, bytes_read = self.socket_read(
                        socket_num, data_length
                    )
                else:
                    bytes_on_socket, bytes_read = self.socket_read(socket_num, length)
                    # just consume the rest, it is lost to the higher layers
                    self.socket_read(socket_num, data_length - length)
        return bytes_on_socket, bytes_read

    def socket_write(
        self, socket_num: int, buffer: bytearray, timeout: float = 0.0
    ) -> int:
        """
        Write data to a socket.

        :param int socket_num: The socket to write to.
        :param bytearray buffer: The data to write to the socket.
        :param float timeout: Write data timeout in seconds, defaults to 0.0 which waits
            indefinitely.

        :return int: The number of bytes written to the socket.

        :raises ConnectionError: If the Ethernet link is down.
        :raises ValueError: If the socket number is out of range.
        :raises RuntimeError: If the data cannot be sent.
        """
        self._sock_num_in_range(socket_num)
        self._check_link_status()
        if len(buffer) > _SOCK_SIZE:
            bytes_to_write = _SOCK_SIZE
        else:
            bytes_to_write = len(buffer)
        stop_time = time.monotonic() + timeout

        # If buffer is available, start the transfer
        free_size = self._get_tx_free_size(socket_num)
        while free_size < bytes_to_write:
            free_size = self._get_tx_free_size(socket_num)
            status = self.socket_status(socket_num)
            if status not in (SNSR_SOCK_ESTABLISHED, SNSR_SOCK_CLOSE_WAIT) or (
                timeout and time.monotonic() > stop_time
            ):
                raise RuntimeError("Unable to write data to the socket.")

        # Read the starting address for saving the transmitting data.
        pointer = self._read_sntx_wr(socket_num)
        offset = pointer & _SOCK_MASK
        self._chip_socket_write(socket_num, offset, bytes_to_write, buffer)
        # update sn_tx_wr to the value + data size
        pointer = (pointer + bytes_to_write) & 0xFFFF
        self._write_sntx_wr(socket_num, pointer)
        self._write_sncr(socket_num, _CMD_SOCK_SEND)

        # check data was  transferred correctly
        while not self.read_snir(socket_num) & _SNIR_SEND_OK:
            if self.socket_status(socket_num) in (
                SNSR_SOCK_CLOSED,
                SNSR_SOCK_TIME_WAIT,
                SNSR_SOCK_FIN_WAIT,
                SNSR_SOCK_CLOSE_WAIT,
                _SNSR_SOCK_CLOSING,
            ):
                raise RuntimeError("No data was sent, socket was closed.")
            if timeout and time.monotonic() > stop_time:
                raise RuntimeError("Operation timed out. No data sent.")
            if self.read_snir(socket_num) & SNIR_TIMEOUT:
                self.write_snir(socket_num, SNIR_TIMEOUT)
                # TCP sockets are closed by the hardware timeout
                # so that will be caught at the while statement.
                # UDP sockets are 1:many so not closed thus return 0.
                if self._read_snmr(socket_num) == SNMR_UDP:
                    return 0
            time.sleep(0.001)
        self.write_snir(socket_num, _SNIR_SEND_OK)
        return bytes_to_write

    def sw_reset(self) -> None:
        """
        Soft reset and reinitialize the WIZnet chip.

        :raises RuntimeError: If reset fails.
        """
        self._wiznet_chip_init()

    def _sw_reset_5x00(self) -> bool:
        """
        Perform a soft reset on the WIZnet 5100s and 5500 chips.

        :returns bool: True if reset was success
        """
        self._write_mr(_MR_RST)
        time.sleep(0.05)
        return self._read_mr() == 0x00

    def _wiznet_chip_init(self) -> None:
        """
        Detect and initialize a WIZnet 5k Ethernet module.

        :raises RuntimeError: If no WIZnet chip is detected.
        """

        def _setup_sockets() -> None:
            """Initialise sockets for w5500 chips."""
            for sock_num in range(_MAX_SOCK_NUM):
                ctrl_byte = 0x0C + (sock_num << 5)
                self._write(0x1E, ctrl_byte, 2)
                self._write(0x1F, ctrl_byte, 2)
            self._ch_base_msb = 0x00
            WIZNET5500._sockets_reserved = [False] * (_MAX_SOCK_NUM - 1)
            self._src_ports_in_use = [0] * _MAX_SOCK_NUM

        def _detect_and_reset_w5500() -> bool:
            """
            Detect and reset a W5500 chip. Called at startup to initialize the
            interface hardware.

            :return bool: True if a W5500 chip is detected, False if not.
            """
            self._chip_type = "w5500"
            if not self._sw_reset_5x00():
                return False

            self._write_mr(0x08)
            if self._read_mr() != 0x08:
                return False

            self._write_mr(0x10)
            if self._read_mr() != 0x10:
                return False

            self._write_mr(0x00)
            if self._read_mr() != 0x00:
                return False

            if self._read(_REG_VERSIONR, 0x00)[0] != 0x04:
                return False
            # Initialize w5500
            _setup_sockets()
            return True

        for func in [
            _detect_and_reset_w5500,
        ]:
            if func():
                return
        self._chip_type = None
        raise RuntimeError("Failed to initialize WIZnet module.")

    def _sock_num_in_range(self, sock: int) -> None:
        """Check that the socket number is in the range 0 - maximum sockets."""
        if not 0 <= sock < self.max_sockets:
            raise ValueError("Socket number out of range.")

    def _check_link_status(self):
        """Raise an exception if the link is down."""
        if not self.link_status:
            raise ConnectionError("The Ethernet connection is down.")

    @staticmethod
    def _read_socket_reservations() -> list[int]:
        """Return the list of reserved sockets."""
        return WIZNET5500._sockets_reserved

    def _read_mr(self) -> int:
        """Read from the Mode Register (MR)."""
        return int.from_bytes(self._read(_REG_MR, 0x00), "big")

    def _write_mr(self, data: int) -> None:
        """Write to the mode register (MR)."""
        self._write(_REG_MR, 0x04, data)

    # *** Low Level Methods ***

    def _read(
        self,
        addr: int,
        callback: int,
        length: int = 1,
    ) -> bytes:
        """
        Read data from a register address.

        :param int addr: Register address to read.
        :param int callback: Callback reference.
        :param int length: Number of bytes to read from the register, defaults to 1.

        :return bytes: Data read from the chip.
        """
        with self._device as bus_device:
            self._chip_read(bus_device, addr, callback)
            self._rxbuf = bytearray(length)
            bus_device.readinto(self._rxbuf)
            return bytes(self._rxbuf)

    def _write(self, addr: int, callback: int, data: Union[int, bytes]) -> None:
        """
        Write data to a register address.

        :param int addr: Destination address.
        :param int callback: Callback reference.
        :param Union[int, bytes] data: Data to write to the register address, if data
            is an integer, it must be 1 or 2 bytes.

        :raises OverflowError: if integer data is more than 2 bytes.
        """
        with self._device as bus_device:
            self._chip_write(bus_device, addr, callback)
            try:
                data = data.to_bytes(1, "big")
            except OverflowError:
                data = data.to_bytes(2, "big")
            except AttributeError:
                pass
            bus_device.write(data)

    def _read_two_byte_sock_reg(self, sock: int, reg_address: int) -> int:
        """Read a two byte socket register."""
        register = self._read_socket_register(sock, reg_address) << 8
        register += self._read_socket_register(sock, reg_address + 1)
        return register

    def _write_two_byte_sock_reg(self, sock: int, reg_address: int, data: int) -> None:
        """Write to a two byte socket register."""
        self._write_socket_register(sock, reg_address, data >> 8 & 0xFF)
        self._write_socket_register(sock, reg_address + 1, data & 0xFF)

    # *** Socket Register Methods ***

    def _get_rx_rcv_size(self, sock: int) -> int:
        """Size of received and saved in socket buffer."""
        val = 0
        val_1 = self._read_snrx_rsr(sock)
        while val != val_1:
            val_1 = self._read_snrx_rsr(sock)
            if val_1 != 0:
                val = self._read_snrx_rsr(sock)
        return val

    def _get_tx_free_size(self, sock: int) -> int:
        """Free size of socket's tx buffer block."""
        val = 0
        val_1 = self._read_sntx_fsr(sock)
        while val != val_1:
            val_1 = self._read_sntx_fsr(sock)
            if val_1 != 0:
                val = self._read_sntx_fsr(sock)
        return val

    def _read_snrx_rd(self, sock: int) -> int:
        """Read socket n RX Read Data Pointer Register."""
        return self._read_two_byte_sock_reg(sock, _REG_SNRX_RD)

    def _write_snrx_rd(self, sock: int, data: int) -> None:
        """Write socket n RX Read Data Pointer Register."""
        self._write_two_byte_sock_reg(sock, _REG_SNRX_RD, data)

    def _read_sntx_wr(self, sock: int) -> int:
        """Read the socket write buffer pointer for socket `sock`."""
        return self._read_two_byte_sock_reg(sock, _REG_SNTX_WR)

    def _write_sntx_wr(self, sock: int, data: int) -> None:
        """Write the socket write buffer pointer for socket `sock`."""
        self._write_two_byte_sock_reg(sock, _REG_SNTX_WR, data)

    def _read_sntx_fsr(self, sock: int) -> int:
        """Read socket n TX Free Size Register"""
        return self._read_two_byte_sock_reg(sock, _REG_SNTX_FSR)

    def _read_snrx_rsr(self, sock: int) -> int:
        """Read socket n Received Size Register"""
        return self._read_two_byte_sock_reg(sock, _REG_SNRX_RSR)

    def _read_sndipr(self, sock) -> bytes:
        """Read socket destination IP address."""
        data = []
        for offset in range(4):
            data.append(
                self._read_socket_register(sock, _REG_SNDIPR + offset)
            )
        return bytes(data)

    def _write_sndipr(self, sock: int, ip_addr: bytes) -> None:
        """Write to socket destination IP Address."""
        for offset, value in enumerate(ip_addr):
            self._write_socket_register(
                sock, _REG_SNDIPR + offset, value
            )

    def _read_sndport(self, sock: int) -> int:
        """Read socket destination port."""
        return self._read_two_byte_sock_reg(sock, _REG_SNDPORT)

    def _write_sndport(self, sock: int, port: int) -> None:
        """Write to socket destination port."""
        self._write_two_byte_sock_reg(sock, _REG_SNDPORT, port)

    def _read_snsr(self, sock: int) -> int:
        """Read Socket n Status Register."""
        return self._read_socket_register(sock, _REG_SNSR)

    def read_snir(self, sock: int) -> int:
        """Read Socket n Interrupt Register."""
        return self._read_socket_register(sock, _REG_SNIR)

    def write_snir(self, sock: int, data: int) -> None:
        """Write to Socket n Interrupt Register."""
        self._write_socket_register(sock, _REG_SNIR, data)

    def _read_snmr(self, sock: int) -> int:
        """Read the socket MR register."""
        return self._read_socket_register(sock, _REG_SNMR)

    def _write_snmr(self, sock: int, protocol: int) -> None:
        """Write to Socket n Mode Register."""
        self._write_socket_register(sock, _REG_SNMR, protocol)

    def _write_sock_port(self, sock: int, port: int) -> None:
        """Write to the socket port number."""
        self._write_two_byte_sock_reg(sock, _REG_SNPORT, port)

    def _write_sncr(self, sock: int, data: int) -> None:
        """Write to socket command register."""
        self._write_socket_register(sock, _REG_SNCR, data)
        # Wait for command to complete before continuing.
        while self._read_socket_register(sock, _REG_SNCR):
            pass

    @property
    def rcr(self) -> int:
        """Retry count register."""
        return int.from_bytes(self._read(_REG_RCR, 0x00), "big")

    @rcr.setter
    def rcr(self, retry_count: int) -> None:
        """Retry count register."""
        if 0 > retry_count > 255:
            raise ValueError("Retries must be from 0 to 255.")
        self._write(_REG_RCR, 0x04, retry_count)

    @property
    def rtr(self) -> int:
        """Retry time register."""
        return int.from_bytes(self._read(_REG_RTR, 0x00, 2), "big")

    @rtr.setter
    def rtr(self, retry_time: int) -> None:
        """Retry time register."""
        if 0 > retry_time >= 2**16:
            raise ValueError("Retry time must be from 0 to 65535")
        self._write(_REG_RTR, 0x04, retry_time)

    # *** Chip Specific Methods ***

    def _chip_read(self, device: "busio.SPI", address: int, call_back: int) -> None:
        """Chip specific calls for _read method."""
        if self._chip_type in ("w5500", "w6100"):
            device.write((address >> 8).to_bytes(1, "big"))
            device.write((address & 0xFF).to_bytes(1, "big"))
            device.write(call_back.to_bytes(1, "big"))
        elif self._chip_type == "w5100s":
            device.write((0x0F).to_bytes(1, "big"))
            device.write((address >> 8).to_bytes(1, "big"))
            device.write((address & 0xFF).to_bytes(1, "big"))

    def _chip_write(self, device: "busio.SPI", address: int, call_back: int) -> None:
        """Chip specific calls for _write."""
        if self._chip_type in ("w5500", "w6100"):
            device.write((address >> 8).to_bytes(1, "big"))
            device.write((address & 0xFF).to_bytes(1, "big"))
            device.write(call_back.to_bytes(1, "big"))
        elif self._chip_type == "w5100s":
            device.write((0xF0).to_bytes(1, "big"))
            device.write((address >> 8).to_bytes(1, "big"))
            device.write((address & 0xFF).to_bytes(1, "big"))

    def _chip_socket_read(self, socket_number, pointer, bytes_to_read):
        """Chip specific calls for socket_read."""
        if self._chip_type in ("w5500", "w6100"):
            # Read data from the starting address of snrx_rd
            ctrl_byte = 0x18 + (socket_number << 5)
            bytes_read = self._read(pointer, ctrl_byte, bytes_to_read)
        elif self._chip_type == "w5100s":
            offset = pointer & _SOCK_MASK
            src_addr = offset + (socket_number * _SOCK_SIZE + 0x6000)
            if offset + bytes_to_read > _SOCK_SIZE:
                split_point = _SOCK_SIZE - offset
                bytes_read = self._read(src_addr, 0x00, split_point)
                split_point = bytes_to_read - split_point
                src_addr = socket_number * _SOCK_SIZE + 0x6000
                bytes_read += self._read(src_addr, 0x00, split_point)
            else:
                bytes_read = self._read(src_addr, 0x00, bytes_to_read)
        return bytes_read

    def _chip_socket_write(
        self, socket_number: int, offset: int, bytes_to_write: int, buffer: bytes
    ):
        """Chip specific calls for socket_write."""
        if self._chip_type in ("w5500", "w6100"):
            dst_addr = offset + (socket_number * _SOCK_SIZE + 0x8000)
            cntl_byte = 0x14 + (socket_number << 5)
            self._write(dst_addr, cntl_byte, buffer[:bytes_to_write])

        elif self._chip_type == "w5100s":
            dst_addr = offset + (socket_number * _SOCK_SIZE + 0x4000)

            if offset + bytes_to_write > _SOCK_SIZE:
                split_point = _SOCK_SIZE - offset
                self._write(dst_addr, 0x00, buffer[:split_point])
                dst_addr = socket_number * _SOCK_SIZE + 0x4000
                self._write(dst_addr, 0x00, buffer[split_point:bytes_to_write])
            else:
                self._write(dst_addr, 0x00, buffer[:bytes_to_write])

    def _chip_parse_udp_header(self, socket_num) -> int:
        """
        Parse chip specific UDP header data for IPv4 packets.

        Sets the source IPv4 address and port number and returns the UDP data length.

        :return int: The UDP data length.
        """
        if self._chip_type in ("w5100s", "w5500"):
            self.udp_from_ip[socket_num] = self._pbuff[:4]
            self.udp_from_port[socket_num] = int.from_bytes(self._pbuff[4:6], "big")
            return int.from_bytes(self._pbuff[6:], "big")
        if self._chip_type == "w6100":
            self.udp_from_ip[socket_num] = self._pbuff[3:7]
            self.udp_from_port[socket_num] = int.from_bytes(self._pbuff[6:], "big")
            return int.from_bytes(self._pbuff[:2], "big") & 0x07FF
        raise ValueError("Unsupported chip type.")

    def _write_socket_register(self, sock: int, address: int, data: int) -> None:
        """Write to a WIZnet 5k socket register."""
        if self._chip_type in ("w5500", "w6100"):
            cntl_byte = (sock << 5) + 0x0C
            self._write(address, cntl_byte, data)
        elif self._chip_type == "w5100s":
            cntl_byte = 0
            self._write(self._ch_base_msb + sock * _CH_SIZE + address, cntl_byte, data)

    def _read_socket_register(self, sock: int, address: int) -> int:
        """Read a WIZnet 5k socket register."""
        if self._chip_type in ("w5500", "w6100"):
            cntl_byte = (sock << 5) + 0x08
            register = self._read(address, cntl_byte)
        elif self._chip_type == "w5100s":
            cntl_byte = 0
            register = self._read(
                self._ch_base_msb + sock * _CH_SIZE + address, cntl_byte
            )
        return int.from_bytes(register, "big")

_the_interface: Optional[WIZNET5500] = None
_default_socket_timeout = None


def _is_ipv4_string(ipv4_address: str) -> bool:
    """Check for a valid IPv4 address in dotted-quad string format
    (for example, "123.45.67.89").

    :param: str ipv4_address: The string to test.

    :return bool: True if a valid IPv4 address, False otherwise.
    """
    octets = ipv4_address.split(".", 3)
    if len(octets) == 4 and "".join(octets).isdigit():
        if all((0 <= int(octet) <= 255 for octet in octets)):
            return True
    return False


def set_interface(iface: WIZNET5500) -> None:
    """
    Helper to set the global internet interface.

    :param wiznet5k.adafruit_wiznet5k.WIZNET5K iface: The ethernet interface.
    """
    global _the_interface  # pylint: disable=global-statement, invalid-name
    _the_interface = iface


def getdefaulttimeout() -> Optional[float]:
    """
    Return the default timeout in seconds for new socket objects. A value of
    None indicates that new socket objects have no timeout. When the socket module is
    first imported, the default is None.
    """
    return _default_socket_timeout


def setdefaulttimeout(timeout: Optional[float]) -> None:
    """
    Set the default timeout in seconds (float) for new socket objects. When the socket
    module is first imported, the default is None. See settimeout() for possible values
    and their respective meanings.

    :param Optional[float] timeout: The default timeout in seconds or None.
    """
    global _default_socket_timeout  # pylint: disable=global-statement
    if timeout is None or (isinstance(timeout, (int, float)) and timeout >= 0):
        _default_socket_timeout = timeout
    else:
        raise ValueError("Timeout must be None, 0.0 or a positive numeric value.")


def htonl(x: int) -> int:
    """
    Convert 32-bit positive integer from host to network byte order.

    :param int x: 32-bit positive integer from host.

    :return int: 32-bit positive integer in network byte order.
    """
    if byteorder == "big":
        return x
    return int.from_bytes(x.to_bytes(4, "little"), "big")


def htons(x: int) -> int:
    """
    Convert 16-bit positive integer from host to network byte order.

    :param int x: 16-bit positive integer from host.

    :return int: 16-bit positive integer in network byte order.
    """
    if byteorder == "big":
        return x
    return ((x << 8) & 0xFF00) | ((x >> 8) & 0xFF)


def inet_aton(ip_address: str) -> bytes:
    """
    Convert an IPv4 address from dotted-quad string format (for example, "123.45.67.89")
    to 32-bit packed binary format, as a bytes object four characters in length. This is
    useful when conversing with a program that uses the standard C library and needs
    objects of type struct in_addr, which is the C type for the 32-bit packed binary this
    function returns.

    :param str ip_address: The IPv4 address to convert.

    :return bytes: The converted IPv4 address.
    """
    if not _is_ipv4_string(ip_address):
        raise ValueError("The IPv4 address must be a dotted-quad string.")
    return _the_interface.unpretty_ip(ip_address)


def inet_ntoa(ip_address: Union[bytes, bytearray]) -> str:
    """
    Convert a 32-bit packed IPv4 address (a bytes-like object four bytes in length) to
    its standard dotted-quad string representation (for example, ‘123.45.67.89’). This is
    useful when conversing with a program that uses the standard C library and needs
    objects of type struct in_addr, which is the C type for the 32-bit packed binary data
    this function takes as an argument.

    :param Union[bytes, bytearray ip_address: The IPv4 address to convert.

    :return str: The converted ip_address:
    """
    if len(ip_address) != 4:
        raise ValueError("The IPv4 address must be 4 bytes.")
    return _the_interface.pretty_ip(ip_address)


SOCK_STREAM = const(0x21)  # TCP
SOCK_DGRAM = const(0x02)  # UDP
AF_INET = const(3)


# pylint: disable=too-many-arguments, unused-argument
def getaddrinfo(
    host: str,
    port: int,
    family: int = 0,
    type: int = 0,
    proto: int = 0,
    flags: int = 0,
) -> List[Tuple[int, int, int, str, Tuple[str, int]]]:
    """
    Translate the host/port argument into a sequence of 5-tuples that contain all the necessary
    arguments for creating a socket connected to that service.

    :param str host: a domain name, a string representation of an IPv4 address or
        None.
    :param int port: Port number to connect to (0 - 65536).
    :param int family: Ignored and hardcoded as 0x03 (the only family implemented) by the function.
    :param int type: The type of socket, either SOCK_STREAM (0x21) for TCP or SOCK_DGRAM (0x02)
        for UDP, defaults to 0.
    :param int proto: Unused in this implementation of socket.
    :param int flags: Unused in this implementation of socket.

    :return List[Tuple[int, int, int, str, Tuple[str, int]]]: Address info entries in the form
        (family, type, proto, canonname, sockaddr). In these tuples, family, type, proto are meant
        to be passed to the socket() function. canonname will always be an empty string, sockaddr
        is a tuple describing a socket address, whose format is (address, port), and is meant to be
        passed to the socket.connect() method.
    """
    if not isinstance(port, int):
        raise ValueError("Port must be an integer")
    if not _is_ipv4_string(host):
        host = gethostbyname(host)
    return [(AF_INET, type, proto, "", (host, port))]


def gethostbyname(hostname: str) -> str:
    """
    Translate a host name to IPv4 address format. The IPv4 address is returned as a string, such
    as '100.50.200.5'. If the host name is an IPv4 address itself it is returned unchanged.

    :param str hostname: Hostname to lookup.

    :return str: IPv4 address (a string of the form '0.0.0.0').
    """
    if _is_ipv4_string(hostname):
        return hostname
    address = _the_interface.get_host_by_name(hostname)
    address = "{}.{}.{}.{}".format(address[0], address[1], address[2], address[3])
    return address

class socket:
    """
    A simplified implementation of the Python 'socket' class for connecting
    to a Wiznet5k module.
    """

    def debug_print(self,statement:str = '') -> None:
        """
        :param statement: message to get printed in debug print
        """
        if self._debug:
            print(co("[SOCKET]" + str(statement), 'blue', 'bold'))

    def __init__(
        self,
        family: int = AF_INET,
        type: int = SOCK_STREAM,
        proto: int = 0,
        fileno: Optional[int] = None,
        debug: bool = True
    ) -> None:
        """
        :param int family: Socket address (and protocol) family, defaults to AF_INET.
        :param int type: Socket type, use SOCK_STREAM for TCP and SOCK_DGRAM for UDP,
            defaults to SOCK_STREAM.
        :param int proto: Unused, retained for compatibility.
        :param Optional[int] fileno: Unused, retained for compatibility.
        """
        self._debug=debug
        if family != AF_INET:
            raise RuntimeError("Only AF_INET family supported by W5K modules.")
        self._socket_closed = False
        self._sock_type = type
        self._buffer = b""
        self._timeout = _default_socket_timeout
        self._listen_port = None

        self._socknum = _the_interface.get_socket(reserve_socket=True)
        if self._socknum == _SOCKET_INVALID:
            raise RuntimeError("Failed to allocate socket.")

    def __del__(self):
        _the_interface.release_socket(self._socknum)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _the_interface.release_socket(self._socknum)
        if self._sock_type == SOCK_STREAM:
            _the_interface.write_snir(
                self._socknum, 0xFF
            )  # Reset socket interrupt register.
            _the_interface.socket_disconnect(self._socknum)
            mask = (
                SNIR_TIMEOUT
                | SNIR_DISCON
            )
            while not _the_interface.read_snir(self._socknum) & mask:
                pass
        _the_interface.write_snir(
            self._socknum, 0xFF
        )  # Reset socket interrupt register.
        _the_interface.socket_close(self._socknum)
        while (
            _the_interface.socket_status(self._socknum)
            != SNSR_SOCK_CLOSED
        ):
            pass

    # This works around problems with using a class method as a decorator.
    def _check_socket_closed(func):  # pylint: disable=no-self-argument
        """Decorator to check whether the socket object has been closed."""

        def wrapper(self, *args, **kwargs):
            if self._socket_closed:  # pylint: disable=protected-access
                raise RuntimeError("The socket has been closed.")
            return func(self, *args, **kwargs)  # pylint: disable=not-callable

        return wrapper

    @property
    def _status(self) -> int:
        """
        Return the status of the socket.

        :return int: Status of the socket.
        """
        return _the_interface.socket_status(self._socknum)

    @property
    def _connected(self) -> bool:
        """
        Return whether connected to the socket.

        :return bool: Whether connected.
        """
        # pylint: disable=protected-access

        if self._socknum >= _the_interface.max_sockets:
            return False
        status = _the_interface.socket_status(self._socknum)
        if (
            status == SNSR_SOCK_CLOSE_WAIT
            and self._available() == 0
        ):
            result = False
        else:
            result = status not in (
                SNSR_SOCK_CLOSED,
                SNSR_SOCK_LISTEN,
                SNSR_SOCK_TIME_WAIT,
                SNSR_SOCK_FIN_WAIT,
            )
        if not result and status != SNSR_SOCK_LISTEN:
            self.close()
        return result

    @_check_socket_closed
    def getpeername(self) -> Tuple[str, int]:
        """
        Return the remote address to which the socket is connected.

        :return Tuple[str, int]: IPv4 address and port the socket is connected to.
        """
        return _the_interface.remote_ip(self._socknum), _the_interface.remote_port(
            self._socknum
        )

    @_check_socket_closed
    def bind(self, address: Tuple[Optional[str], int]) -> None:
        """
        Bind the socket to address. The socket must not already be bound.

        The hardware sockets on WIZNET5K systems all share the same IPv4 address. The
        address is assigned at startup. Ports can only be bound to this address.

        :param Tuple[Optional[str], int] address: Address as a (host, port) tuple.

        :raises ValueError: If the IPv4 address specified is not the address
            assigned to the WIZNET5K interface.
        """
        # Check to see if the socket is bound.
        if self._listen_port:
            raise ConnectionError("The socket is already bound.")
        self._bind(address)

    def _bind(self, address: Tuple[Optional[str], int]) -> None:
        """
        Helper function to allow bind() to check for an existing connection and for
        accept() to generate a new socket connection.

        :param Tuple[Optional[str], int] address: Address as a (host, port) tuple.
        """
        if address[0]:
            if gethostbyname(address[0]) != _the_interface.pretty_ip(
                _the_interface.ip_address
            ):
                raise ValueError(
                    "The IPv4 address requested must match {}, "
                    "the one assigned to the WIZNET5K interface.".format(
                        _the_interface.pretty_ip(_the_interface.ip_address)
                    )
                )
        self._listen_port = address[1]
        # For UDP servers we need to open the socket here because we won't call
        # listen
        if self._sock_type == SOCK_DGRAM:
            _the_interface.socket_listen(
                self._socknum,
                self._listen_port,
                SNMR_UDP,
            )
            self._buffer = b""

    @_check_socket_closed
    def listen(self, backlog: int = 0) -> None:
        """
        Enable a server to accept connections.

        :param int backlog: Included for compatibility but ignored.
        """
        if self._listen_port is None:
            raise RuntimeError("Use bind to set the port before listen!")
        _the_interface.socket_listen(self._socknum, self._listen_port)
        self._buffer = b""

    @_check_socket_closed
    def accept(
        self,
    ) -> Tuple[socket, Tuple[str, int]]:
        """
        Accept a connection. The socket must be bound to an address and listening for connections.

        :return Tuple[socket, Tuple[str, int]]: The return value is a pair
            (conn, address) where conn is a new socket object to send and receive data on
            the connection, and address is the address bound to the socket on the other
            end of the connection.
        """
        stamp = time.monotonic()
        while self._status not in (
            SNSR_SOCK_SYNRECV,
            SNSR_SOCK_ESTABLISHED,
        ):
            self.debug_print("SNSR: " + str(self._status))
            if self._timeout and 0 < self._timeout < time.monotonic() - stamp:
                raise TimeoutError("Failed to accept connection.")
            if self._status == SNSR_SOCK_CLOSED:
                self.debug_print("Socket closed!")
                self.close()
                self.listen()
        self.debug_print("SYN receievd or socket established!")
        _, addr = _the_interface.socket_accept(self._socknum)
        current_socknum = self._socknum
        # Create a new socket object and swap socket nums, so we can continue listening
        client_sock = socket()
        self._socknum = client_sock._socknum  # pylint: disable=protected-access
        client_sock._socknum = current_socknum  # pylint: disable=protected-access
        self._bind((None, self._listen_port))
        self.listen()
        while self._status != SNSR_SOCK_LISTEN:
            raise RuntimeError("Failed to open new listening socket")
        return client_sock, addr

    @_check_socket_closed
    def connect(self, address: Tuple[str, int]) -> None:
        """
        Connect to a remote socket at address.

        :param Tuple[str, int] address: Remote socket as a (host, port) tuple.
        """
        if self._listen_port is not None:
            _the_interface.src_port = self._listen_port
        result = _the_interface.socket_connect(
            self._socknum,
            _the_interface.unpretty_ip(gethostbyname(address[0])),
            address[1],
            self._sock_type,
        )
        _the_interface.src_port = 0
        if not result:
            raise RuntimeError("Failed to connect to host ", address[0])
        self._buffer = b""

    @_check_socket_closed
    def send(self, data: Union[bytes, bytearray]) -> int:
        """
        Send data to the socket. The socket must be connected to a remote socket.
        Applications are responsible for checking that all data has been sent; if
        only some of the data was transmitted, the application needs to attempt
        delivery of the remaining data.

        :param bytearray data: Data to send to the socket.

        :return int: Number of bytes sent.
        """
        timeout = 0 if self._timeout is None else self._timeout
        bytes_sent = _the_interface.socket_write(self._socknum, data, timeout)
        gc.collect()
        return bytes_sent

    @_check_socket_closed
    def sendto(self, data: bytearray, *flags_and_or_address: any) -> int:
        """
        Send data to the socket. The socket should not be connected to a remote socket, since the
        destination socket is specified by address. Return the number of bytes sent..

        Either:
        :param bytearray data: Data to send to the socket.
        :param [Tuple[str, int]] address: Remote socket as a (host, port) tuple.

        Or:
        :param bytearray data: Data to send to the socket.
        :param int flags: Not implemented, kept for compatibility.
        :param Tuple[int, Tuple(str, int)] address: Remote socket as a (host, port) tuple
        """
        # May be called with (data, address) or (data, flags, address)
        other_args = list(flags_and_or_address)
        if len(other_args) in (1, 2):
            address = other_args[-1]
        else:
            raise ValueError("Incorrect number of arguments, should be 2 or 3.")
        self.connect(address)
        return self.send(data)

    @_check_socket_closed
    def recv(
        # pylint: disable=too-many-branches
        self,
        bufsize: int,
        flags: int = 0,
    ) -> bytes:
        """
        Receive data from the socket. The return value is a bytes object representing the data
        received. The maximum amount of data to be received at once is specified by bufsize.

        :param int bufsize: Maximum number of bytes to receive.
        :param int flags: ignored, present for compatibility.

        :return bytes: Data from the socket.
        """
        stamp = time.monotonic()
        while not self._available():
            if self._timeout and 0 < self._timeout < time.monotonic() - stamp:
                break
            time.sleep(0.05)
        bytes_on_socket = self._available()
        if not bytes_on_socket:
            return b""
        bytes_to_read = min(bytes_on_socket, bufsize)
        if self._sock_type == SOCK_STREAM:
            bytes_read = _the_interface.socket_read(self._socknum, bytes_to_read)[1]
        else:
            bytes_read = _the_interface.read_udp(self._socknum, bytes_to_read)[1]
        gc.collect()
        return bytes(bytes_read)

    def _embed_recv(
        self, bufsize: int = 0, flags: int = 0
    ) -> bytes:  # pylint: disable=too-many-branches
        """
        Read from the connected remote address.

        :param int bufsize: Maximum number of bytes to receive, ignored by the
            function, defaults to 0.
        :param int flags: ignored, present for compatibility.

        :return bytes: All data available from the connection.
        """
        avail = self._available()
        if avail:
            if self._sock_type == SOCK_STREAM:
                self._buffer += _the_interface.socket_read(self._socknum, avail)[1]
            elif self._sock_type == SOCK_DGRAM:
                self._buffer += _the_interface.read_udp(self._socknum, avail)[1]
        gc.collect()
        ret = self._buffer
        self._buffer = b""
        gc.collect()
        return ret

    @_check_socket_closed
    def recvfrom(self, bufsize: int, flags: int = 0) -> Tuple[bytes, Tuple[str, int]]:
        """
        Receive data from the socket. The return value is a pair (bytes, address) where bytes is
        a bytes object representing the data received and address is the address of the socket
        sending the data.

        :param int bufsize: Maximum number of bytes to receive.
        :param int flags: Ignored, present for compatibility.

        :return Tuple[bytes, Tuple[str, int]]: a tuple (bytes, address)
            where address is a tuple (address, port)
        """
        return (
            self.recv(bufsize),
            (
                _the_interface.pretty_ip(_the_interface.udp_from_ip[self._socknum]),
                _the_interface.udp_from_port[self._socknum],
            ),
        )

    @_check_socket_closed
    def recv_into(self, buffer: bytearray, nbytes: int = 0, flags: int = 0) -> int:
        """
        Receive up to nbytes bytes from the socket, storing the data into a buffer
        rather than creating a new bytestring.

        :param bytearray buffer: Data buffer to read into.
        :param nbytes: Maximum number of bytes to receive (if 0, use length of buffer).
        :param int flags: ignored, present for compatibility.

        :return int: the number of bytes received
        """
        if nbytes == 0:
            nbytes = len(buffer)
        bytes_received = self.recv(nbytes)
        nbytes = len(bytes_received)
        buffer[:nbytes] = bytes_received
        return nbytes

    @_check_socket_closed
    def recvfrom_into(
        self, buffer: bytearray, nbytes: int = 0, flags: int = 0
    ) -> Tuple[int, Tuple[str, int]]:
        """
        Receive data from the socket, writing it into buffer instead of creating a new bytestring.
        The return value is a pair (nbytes, address) where nbytes is the number of bytes received
        and address is the address of the socket sending the data.

        :param bytearray buffer: Data buffer.
        :param int nbytes: Maximum number of bytes to receive.
        :param int flags: Unused, present for compatibility.

        :return Tuple[int, Tuple[str, int]]: The number of bytes and address.
        """
        return (
            self.recv_into(buffer, nbytes),
            (
                _the_interface.remote_ip(self._socknum),
                _the_interface.remote_port(self._socknum),
            ),
        )

    def _readline(self) -> bytes:
        """
        Read a line from the socket.

        Deprecated, will be removed in the future.

        Attempt to return as many bytes as we can up to but not including a carriage return and
        linefeed character pair.

        :return bytes: The data read from the socket.
        """
        stamp = time.monotonic()
        while b"\r\n" not in self._buffer:
            avail = self._available()
            if avail:
                if self._sock_type == SOCK_STREAM:
                    self._buffer += _the_interface.socket_read(self._socknum, avail)[1]
                elif self._sock_type == SOCK_DGRAM:
                    self._buffer += _the_interface.read_udp(self._socknum, avail)[1]
                if (
                    self._timeout
                    and not avail
                    and 0 < self._timeout < time.monotonic() - stamp
                ):
                    self.close()
                    raise RuntimeError("Didn't receive response, failing out...")
        firstline, self._buffer = self._buffer.split(b"\r\n", 1)
        gc.collect()
        return firstline

    def _disconnect(self) -> None:
        """Disconnect a TCP socket."""
        if self._sock_type != SOCK_STREAM:
            raise RuntimeError("Socket must be a TCP socket.")
        _the_interface.socket_disconnect(self._socknum)

    @_check_socket_closed
    def close(self) -> None:
        """
        Mark the socket closed. Once that happens, all future operations on the socket object
        will fail. The remote end will receive no more data.
        """
        _the_interface.release_socket(self._socknum)
        _the_interface.socket_close(self._socknum)
        self._socket_closed = True

    def _available(self) -> int:
        """
        Return how many bytes of data are available to be read from the socket.

        :return int: Number of bytes available.
        """
        return _the_interface.socket_available(self._socknum, self._sock_type)

    @_check_socket_closed
    def settimeout(self, value: Optional[float]) -> None:
        """
        Set a timeout on blocking socket operations. The value argument can be a
        non-negative floating point number expressing seconds, or None. If a non-zero
        value is given, subsequent socket operations will raise a timeout exception
        if the timeout period value has elapsed before the operation has completed.
        If zero is given, the socket is put in non-blocking mode. If None is given,
        the socket is put in blocking mode..

        :param Optional[float] value: Socket read timeout in seconds.
        """
        if value is None or (isinstance(value, (int, float)) and value >= 0):
            self._timeout = value
        else:
            raise ValueError("Timeout must be None, 0.0 or a positive numeric value.")

    @_check_socket_closed
    def gettimeout(self) -> Optional[float]:
        """
        Return the timeout in seconds (float) associated with socket operations, or None if no
        timeout is set. This reflects the last call to setblocking() or settimeout().

        :return Optional[float]: Timeout in seconds, or None if no timeout is set.
        """
        return self._timeout

    @_check_socket_closed
    def setblocking(self, flag: bool) -> None:
        """
        Set blocking or non-blocking mode of the socket: if flag is false, the socket is set
        to non-blocking, else to blocking mode.

        This method is a shorthand for certain settimeout() calls:

        sock.setblocking(True) is equivalent to sock.settimeout(None)
        sock.setblocking(False) is equivalent to sock.settimeout(0.0)

        :param bool flag: The blocking mode of the socket.

        :raises TypeError: If flag is not a bool.

        """
        if flag is True:
            self.settimeout(None)
        elif flag is False:
            self.settimeout(0.0)
        else:
            raise TypeError("Flag must be a boolean.")

    @_check_socket_closed
    def getblocking(self) -> bool:
        """
        Return True if socket is in blocking mode, False if in non-blocking.

        This is equivalent to checking socket.gettimeout() == 0.

        :return bool: Blocking mode of the socket.
        """
        return self.gettimeout() == 0

    @property
    @_check_socket_closed
    def family(self) -> int:
        """Socket family (always 0x03 in this implementation)."""
        return 3

    @property
    @_check_socket_closed
    def type(self):
        """Socket type."""
        return self._sock_type

    @property
    @_check_socket_closed
    def proto(self):
        """Socket protocol (always 0x00 in this implementation)."""
        return 0