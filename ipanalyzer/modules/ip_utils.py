"""IP utilities with IPv4/IPv6 support"""
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address
from typing import List


class IPUtils:
    @staticmethod
    def is_valid_ip(addr: str) -> bool:
        try:
            ip_address(addr)
            return True
        except Exception:
            return False

    @staticmethod
    def is_ipv4(addr: str) -> bool:
        try:
            return isinstance(ip_address(addr), IPv4Address)
        except Exception:
            return False

    @staticmethod
    def is_ipv6(addr: str) -> bool:
        try:
            return isinstance(ip_address(addr), IPv6Address)
        except Exception:
            return False

    @staticmethod
    def parse_cidr(cidr: str):
        net = ip_network(cidr, strict=False)
        return {
            "network": str(net.network_address),
            "netmask": str(net.netmask),
            "prefixlen": net.prefixlen,
            "broadcast": str(net.broadcast_address) if hasattr(net, 'broadcast_address') else None,
            "total": net.num_addresses,
        }

    @staticmethod
    def get_usable_ips(cidr: str) -> List[str]:
        net = ip_network(cidr, strict=False)
        # For IPv4 exclude network and broadcast when possible
        if isinstance(net.network_address, IPv4Address) and net.num_addresses > 2:
            return [str(ip) for ip in net.hosts()]
        return [str(ip) for ip in net]
"""
IP Utility Functions
Core utilities for IP address parsing and validation
"""

import re
import socket
import struct
import ipaddress
from typing import Tuple, List, Dict, Optional


class IPValidator:
    """Validate and parse IP addresses"""
    
    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """Check if string is valid IPv4 address"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        if not match:
            return False
        for octet in match.groups():
            if int(octet) > 255:
                return False
        return True
    
    @staticmethod
    def is_valid_cidr(cidr: str) -> bool:
        """Check if string is valid CIDR notation"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
        match = re.match(pattern, cidr)
        if not match:
            return False
        ip_parts = match.groups()[:4]
        prefix = int(match.groups()[4])
        
        for octet in ip_parts:
            if int(octet) > 255:
                return False
        if prefix < 0 or prefix > 32:
            return False
        return True


class IPConverter:
    """Convert between IP formats"""
    
    @staticmethod
    def ip_to_int(ip: str) -> int:
        """Convert IP address to integer"""
        try:
            return struct.unpack('>I', socket.inet_aton(ip))[0]
        except (socket.error, TypeError):
            raise ValueError(f"Invalid IP address: {ip}")
    
    @staticmethod
    def int_to_ip(num: int) -> str:
        """Convert integer to IP address"""
        return socket.inet_ntoa(struct.pack('>I', num))


class CIDRCalculator:
    """Calculate CIDR ranges and subnet information"""
    
    @staticmethod
    def parse_cidr(cidr: str) -> Tuple[str, str, str, int]:
        """
        Parse CIDR notation
        Returns: (network_ip, broadcast_ip, netmask, prefix_length)
        """
        ip, prefix = cidr.split('/')
        prefix = int(prefix)
        
        # Calculate netmask
        mask_bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        netmask = IPConverter.int_to_ip(mask_bits)
        
        # Calculate network IP
        ip_int = IPConverter.ip_to_int(ip)
        network_int = ip_int & mask_bits
        network_ip = IPConverter.int_to_ip(network_int)
        
        # Calculate broadcast IP
        broadcast_int = network_int | (~mask_bits & 0xFFFFFFFF)
        broadcast_ip = IPConverter.int_to_ip(broadcast_int)
        
        return network_ip, broadcast_ip, netmask, prefix
    
    @staticmethod
    def get_ip_range(cidr: str) -> Tuple[int, int]:
        """Get range of usable IPs in CIDR block"""
        network_ip, broadcast_ip, _, _ = CIDRCalculator.parse_cidr(cidr)
        return IPConverter.ip_to_int(network_ip), IPConverter.ip_to_int(broadcast_ip)
    
    @staticmethod
    def get_usable_ips(cidr: str) -> List[str]:
        """Get all usable IPs in CIDR block (excluding network and broadcast)"""
        start_int, end_int = CIDRCalculator.get_ip_range(cidr)
        # Exclude network address and broadcast address
        if end_int - start_int > 2:
            return [IPConverter.int_to_ip(i) for i in range(start_int + 1, end_int)]
        return []
    
    @staticmethod
    def subnets_from_cidr(cidr: str, subnet_prefix: int) -> List[str]:
        """Divide CIDR block into smaller subnets"""
        network_ip, _, _, original_prefix = CIDRCalculator.parse_cidr(cidr)
        
        if subnet_prefix <= original_prefix:
            return [cidr]
        
        subnets = []
        ip_int = IPConverter.ip_to_int(network_ip)
        num_subnets = 2 ** (subnet_prefix - original_prefix)
        step = 2 ** (32 - subnet_prefix)
        
        for i in range(num_subnets):
            subnet_ip = IPConverter.int_to_ip(ip_int + i * step)
            subnets.append(f"{subnet_ip}/{subnet_prefix}")
        
        return subnets


class IPClassifier:
    """Classify IP addresses"""
    
    PRIVATE_RANGES = [
        (IPConverter.ip_to_int("10.0.0.0"), IPConverter.ip_to_int("10.255.255.255")),
        (IPConverter.ip_to_int("172.16.0.0"), IPConverter.ip_to_int("172.31.255.255")),
        (IPConverter.ip_to_int("192.168.0.0"), IPConverter.ip_to_int("192.168.255.255")),
    ]
    
    @staticmethod
    def is_private(ip: str) -> bool:
        """Check if IP is private (RFC 1918)"""
        ip_int = IPConverter.ip_to_int(ip)
        for start, end in IPClassifier.PRIVATE_RANGES:
            if start <= ip_int <= end:
                return True
        return False
    
    @staticmethod
    def is_loopback(ip: str) -> bool:
        """Check if IP is loopback address"""
        ip_int = IPConverter.ip_to_int(ip)
        return 2130706432 <= ip_int <= 2147483647  # 127.0.0.0/8
    
    @staticmethod
    def is_link_local(ip: str) -> bool:
        """Check if IP is link-local (169.254.0.0/16)"""
        ip_int = IPConverter.ip_to_int(ip)
        return 2851995648 <= ip_int <= 2852061183
    
    @staticmethod
    def classify(ip: str) -> str:
        """Classify IP address"""
        if IPClassifier.is_loopback(ip):
            return "Loopback"
        elif IPClassifier.is_link_local(ip):
            return "Link-Local"
        elif IPClassifier.is_private(ip):
            return "Private"
        else:
            return "Public"


class IPv6Utils:
    """Basic IPv6 utilities using the standard library's ipaddress module."""

    @staticmethod
    def is_valid_ipv6(address: str) -> bool:
        try:
            ipaddress.IPv6Address(address)
            return True
        except Exception:
            return False

    @staticmethod
    def normalize_ipv6(address: str) -> str:
        """Return the fully expanded IPv6 address string."""
        try:
            return ipaddress.IPv6Address(address).exploded
        except Exception:
            raise ValueError(f"Invalid IPv6 address: {address}")

    @staticmethod
    def compress_ipv6(address: str) -> str:
        """Return the compressed (shortest) form of an IPv6 address."""
        try:
            return ipaddress.IPv6Address(address).compressed
        except Exception:
            raise ValueError(f"Invalid IPv6 address: {address}")

    @staticmethod
    def ipv6_to_int(address: str) -> int:
        try:
            return int(ipaddress.IPv6Address(address))
        except Exception:
            raise ValueError(f"Invalid IPv6 address: {address}")

    @staticmethod
    def int_to_ipv6(value: int) -> str:
        try:
            return str(ipaddress.IPv6Address(value))
        except Exception:
            raise ValueError(f"Invalid IPv6 integer: {value}")
