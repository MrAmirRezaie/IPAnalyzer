"""WHOIS analyzer using WHOIS protocol (port 43) with basic referral handling."""
import socket
from typing import Optional


class WHOISAnalyzer:
    DEFAULT_PORT = 43

    def _query_server(self, server: str, query: str, timeout: int = 5) -> str:
        resp = []
        try:
            with socket.create_connection((server, self.DEFAULT_PORT), timeout=timeout) as s:
                s.sendall((query + '\r\n').encode('utf-8'))
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    resp.append(data.decode('utf-8', errors='replace'))
        except Exception as e:
            return f"ERROR: {e}"
        return ''.join(resp)

    def lookup(self, ip: str) -> dict:
        # First query IANA for referral
        iana = self._query_server('whois.iana.org', ip)
        # find refer or whois server in response
        refer = None
        for line in iana.splitlines():
            if line.lower().startswith('refer:') or line.lower().startswith('whois:'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    refer = parts[1].strip()
                    break

        if not refer:
            # fallback to ARIN
            refer = 'whois.arin.net'

        resp = self._query_server(refer, ip)
        return {'ip': ip, 'server': refer, 'raw': resp}
"""
WHOIS Analyzer Module
Offline WHOIS lookup using built-in data and socket communication
"""

import socket
import re
from typing import Dict, Optional
from datetime import datetime
import json
import os


class WHOISAnalyzer:
    """Analyze IP WHOIS information"""
    
    # WHOIS server mapping for different RIRs
    WHOIS_SERVERS = {
        'ARIN': 'whois.arin.net',  # North America
        'RIPE': 'whois.ripe.net',  # Europe
        'APNIC': 'whois.apnic.net',  # Asia-Pacific
        'LACNIC': 'whois.lacnic.net',  # Latin America
        'AFNIC': 'whois.afnic.fr',  # Africa
    }
    
    # Built-in IP ranges database (expanded version)
    IP_RANGES_DB = {
        'ARIN': [
            {'range': '1.0.0.0/24', 'org': 'APNIC', 'country': 'AU'},
            {'range': '1.1.1.0/24', 'org': 'APNIC', 'country': 'AU'},
            {'range': '8.0.0.0/7', 'org': 'Level 3 Communications', 'country': 'US'},
            {'range': '10.0.0.0/8', 'org': 'Private-Use', 'country': 'PRIVATE'},
        ],
        'RIPE': [
            {'range': '2.0.0.0/7', 'org': 'RIPE NCC', 'country': 'EU'},
            {'range': '5.0.0.0/8', 'org': 'RIPE NCC', 'country': 'EU'},
        ],
        'APNIC': [
            {'range': '27.0.0.0/8', 'org': 'APNIC', 'country': 'AU'},
            {'range': '58.0.0.0/8', 'org': 'APNIC', 'country': 'CN'},
        ],
    }
    
    # Country codes database
    COUNTRY_DB = {
        'US': 'United States',
        'AU': 'Australia',
        'CN': 'China',
        'IN': 'India',
        'EU': 'European Union',
        'GB': 'United Kingdom',
        'DE': 'Germany',
        'FR': 'France',
        'JP': 'Japan',
        'BR': 'Brazil',
        'PRIVATE': 'Private Network',
    }
    
    def __init__(self):
        """Initialize WHOIS Analyzer"""
        self.cache = {}
    
    def ip_to_asn_range(self, ip: str) -> Optional[Dict]:
        """
        Determine which ASN/RIR range an IP belongs to
        Using built-in database when possible
        """
        from .ip_utils import IPConverter
        
        ip_int = IPConverter.ip_to_int(ip)
        
        # Check built-in database first
        for rir, ranges in self.IP_RANGES_DB.items():
            for entry in ranges:
                range_ip, prefix = entry['range'].split('/')
                prefix = int(prefix)
                mask_bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                range_int = IPConverter.ip_to_int(range_ip)
                
                if (ip_int & mask_bits) == (range_int & mask_bits):
                    return {
                        'rir': rir,
                        'range': entry['range'],
                        'organization': entry['org'],
                        'country': entry['country'],
                        'source': 'local_database'
                    }
        
        return None
    
    def query_whois_socket(self, ip: str, server: str = 'whois.arin.net') -> Optional[str]:
        """
        Query WHOIS server via socket (offline capable)
        Returns raw WHOIS response
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((server, 43))
            sock.send(f"{ip}\r\n".encode())
            
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            
            sock.close()
            return response.decode('utf-8', errors='ignore')
        except (socket.error, socket.timeout) as e:
            return None
    
    def parse_whois_response(self, response: str) -> Dict:
        """Parse WHOIS response into structured data"""
        data = {
            'organization': None,
            'country': None,
            'network': None,
            'netname': None,
            'description': None,
            'admin_contact': None,
            'tech_contact': None,
            'created': None,
            'updated': None,
            'raw': response
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Organization:') or line.startswith('OrgName:'):
                data['organization'] = line.split(':', 1)[1].strip()
            elif line.startswith('Country:') or line.startswith('OC:'):
                data['country'] = line.split(':', 1)[1].strip()
            elif line.startswith('CIDR:') or line.startswith('NetRange:'):
                data['network'] = line.split(':', 1)[1].strip()
            elif line.startswith('NetName:'):
                data['netname'] = line.split(':', 1)[1].strip()
            elif line.startswith('Comment:') or line.startswith('Descr:'):
                data['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Created:') or line.startswith('RegDate:'):
                data['created'] = line.split(':', 1)[1].strip()
            elif line.startswith('Updated:') or line.startswith('Updated:'):
                data['updated'] = line.split(':', 1)[1].strip()
        
        return data
    
    def analyze_ip(self, ip: str) -> Dict:
        """
        Comprehensive IP analysis
        Returns WHOIS information and IP classification
        """
        if ip in self.cache:
            return self.cache[ip]
        
        from .ip_utils import IPClassifier
        
        result = {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'classification': IPClassifier.classify(ip),
            'is_private': IPClassifier.is_private(ip),
            'is_loopback': IPClassifier.is_loopback(ip),
            'is_link_local': IPClassifier.is_link_local(ip),
            'whois': {}
        }
        
        # Try built-in database first
        asn_info = self.ip_to_asn_range(ip)
        if asn_info:
            result['whois'] = asn_info
            result['whois']['source'] = 'local_database'
        else:
            # If not private, try to query actual WHOIS (if network available)
            if not result['is_private']:
                try:
                    response = self.query_whois_socket(ip)
                    if response:
                        result['whois'] = self.parse_whois_response(response)
                        result['whois']['source'] = 'live_whois'
                    else:
                        result['whois']['source'] = 'unavailable'
                except:
                    result['whois']['source'] = 'unavailable'
        
        self.cache[ip] = result
        return result
    
    def get_bulk_analysis(self, ips: list) -> list:
        """Analyze multiple IPs"""
        return [self.analyze_ip(ip) for ip in ips]
    
    def get_country_name(self, country_code: str) -> str:
        """Get full country name from code"""
        return self.COUNTRY_DB.get(country_code, country_code)
