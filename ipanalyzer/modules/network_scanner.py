"""Basic network scanner stubs (ARP/ping placeholders)."""
import ipaddress
from typing import List


class NetworkScanner:
    def scan_network(self, cidr: str) -> List[dict]:
        # Placeholder: return list of addresses in the network (first 10)
        net = ipaddress.ip_network(cidr, strict=False)
        out = []
        for i, ip in enumerate(net.hosts()):
            out.append({'ip': str(ip), 'mac': None, 'hostname': None})
            if i >= 9:
                break
        return out

    def scan_ports(self, host: str, ports=None) -> List[int]:
        # Lightweight port scan using socket is possible but kept simple here
        if ports is None:
            ports = [22, 80, 443]
        return []
"""
Network Scanner Module
Discover and list connected devices on a network
"""

import subprocess
import re
import platform
import socket
import struct
from typing import List, Dict, Optional
from threading import Thread, Lock
import queue


class NetworkScanner:
    """Scan network for connected devices"""
    
    def __init__(self):
        """Initialize Network Scanner"""
        self.os_type = platform.system()
        self.devices = []
        self.lock = Lock()
    
    def get_local_ip(self) -> Optional[str]:
        """Get local machine IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None
    
    def get_gateway(self) -> Optional[str]:
        """Get default gateway IP"""
        try:
            if self.os_type == 'Windows':
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Default Gateway' in line:
                        return line.split(':')[1].strip().split()[0]
            else:
                result = subprocess.run(['route', '-n'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if '0.0.0.0' in line:
                        parts = line.split()
                        return parts[2]
        except:
            pass
        return None
    
    def ping_host(self, ip: str, timeout: int = 1) -> bool:
        """Check if host is reachable via ping"""
        try:
            if self.os_type == 'Windows':
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), ip],
                    capture_output=True,
                    timeout=timeout + 1
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout * 1000), ip],
                    capture_output=True,
                    timeout=timeout + 1
                )
            return result.returncode == 0
        except:
            return False
    
    def arp_scan(self) -> List[Dict]:
        """
        Scan network using ARP
        Returns list of discovered devices
        """
        devices = []
        try:
            if self.os_type == 'Windows':
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                
                # Parse ARP table
                pattern = r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:]{17})'
                for line in lines:
                    match = re.search(pattern, line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2)
                        
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'method': 'arp',
                            'status': 'active'
                        })
            else:
                result = subprocess.run(['arp', '-n'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                
                pattern = r'(\d+\.\d+\.\d+\.\d+)\s+[^(]*\(([0-9a-fA-F:]{17})\)'
                for line in lines:
                    match = re.search(pattern, line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2)
                        
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'method': 'arp',
                            'status': 'active'
                        })
        except Exception as e:
            pass
        
        return devices
    
    def resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP to hostname"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
    
    def get_mac_vendor(self, mac: str) -> str:
        """Get MAC vendor name (simplified - can be expanded with OUI database)"""
        # Common vendor prefixes
        vendors = {
            '00:50:F2': 'Microsoft',
            '00:0C:29': 'VMware',
            '08:00:27': 'VirtualBox',
            '52:54:00': 'KVM',
            '00:1A:92': 'Netgear',
            '00:1F:3A': 'Apple',
            'B8:27:EB': 'Raspberry Pi',
        }
        
        prefix = mac[:8].upper()
        return vendors.get(prefix, 'Unknown')
    
    def scan_network(self, network_range: str = None) -> List[Dict]:
        """
        Scan local network for connected devices
        network_range: optional CIDR notation (e.g., '192.168.1.0/24')
        """
        devices = []
        
        # First try ARP scan (fastest and most reliable)
        devices = self.arp_scan()
        
        # For each device, try to get more info
        for device in devices:
            hostname = self.resolve_hostname(device['ip'])
            vendor = self.get_mac_vendor(device['mac'])
            
            device['hostname'] = hostname
            device['vendor'] = vendor
        
        # If no devices found via ARP, try ping scan
        if not devices and network_range:
            from .ip_utils import CIDRCalculator
            try:
                usable_ips = CIDRCalculator.get_usable_ips(network_range)
                for ip in usable_ips:
                    if self.ping_host(ip):
                        devices.append({
                            'ip': ip,
                            'mac': 'N/A',
                            'hostname': self.resolve_hostname(ip),
                            'vendor': 'N/A',
                            'method': 'ping',
                            'status': 'reachable'
                        })
            except:
                pass
        
        self.devices = devices
        return devices
    
    def scan_ports(self, ip: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan common ports on a device
        Returns list of open ports
        """
        if ports is None:
            ports = [22, 80, 443, 3389, 5900, 8080, 8443]
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append({
                        'port': port,
                        'service': self.get_service_name(port),
                        'status': 'open'
                    })
            except:
                pass
        
        return open_ports
    
    @staticmethod
    def get_service_name(port: int) -> str:
        """Get common service name for port"""
        services = {
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            3389: 'RDP',
            5900: 'VNC',
            8080: 'HTTP-Proxy',
            8443: 'HTTPS-Alt',
            25: 'SMTP',
            53: 'DNS',
            110: 'POP3',
            143: 'IMAP',
            3306: 'MySQL',
            5432: 'PostgreSQL',
            6379: 'Redis',
            27017: 'MongoDB',
        }
        return services.get(port, 'Unknown')
    
    def get_network_info(self) -> Dict:
        """Get current network information"""
        local_ip = self.get_local_ip()
        gateway = self.get_gateway()
        
        # Calculate network range (assuming /24)
        if local_ip:
            parts = local_ip.split('.')
            network_range = f"{'.'.join(parts[:3])}.0/24"
        else:
            network_range = None
        
        return {
            'local_ip': local_ip,
            'gateway': gateway,
            'estimated_range': network_range,
            'os': self.os_type
        }
