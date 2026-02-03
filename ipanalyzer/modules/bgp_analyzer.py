"""Lightweight BGP analyzer (placeholder for real BGP data parsing)."""
import ipaddress


class BGPAnalyzer:
    def __init__(self, source_file: str = None):
        # source_file can be a path to a BGP dump; for now we keep a small cache
        self.source = source_file

    def get_asn_for_ip(self, ip: str) -> dict:
        # Minimal ASN mapping placeholder: use simple rules for private vs public
        try:
            ipa = ipaddress.ip_address(ip)
        except Exception:
            return {'error': 'invalid_ip'}

        if ipa.is_private:
            return {'ip': ip, 'asn': None, 'description': 'private'}

        # Mocked ASN assignment based on octet for demo
        if ipa.version == 4:
            first = int(str(ipa).split('.')[0])
            asn = 64512 + (first % 100)
            return {'ip': ip, 'asn': f'AS{asn}', 'prefix': 'mocked'}

        return {'ip': ip, 'asn': 'AS0', 'prefix': 'mocked'}
"""
BGP Analyzer - Border Gateway Protocol routing information module
Provides offline BGP route analysis with AS number lookup and path tracing.
"""
from typing import Dict, List, Optional, Tuple, Set
from ipanalyzer.modules.ip_utils import IPConverter


class BGPAnalyzer:
    """
    Comprehensive BGP analyzer for network routing information.
    
    Performs longest-prefix matching against a BGP prefix table to identify
    the origin Autonomous System (AS) for any given IP address. Includes
    AS information lookup, route path analysis, and BGP community support.
    
    Works completely offline using a sample BGP prefix table that can be
    extended with real BGP data from RIPE NCC or RouteViews.
    """

    # Comprehensive BGP prefix table
    # Each entry: (start_int, end_int, asn, as_name, origin, community)
    _SAMPLE_PREFIXES = [
        # Google
        (IPConverter.ip_to_int('8.8.8.0'), IPConverter.ip_to_int('8.8.8.255'),
         15169, 'GOOGLE', 'IGP', 'google:65000'),
        (IPConverter.ip_to_int('8.8.4.0'), IPConverter.ip_to_int('8.8.4.255'),
         15169, 'GOOGLE', 'IGP', 'google:65000'),
        
        # Cloudflare
        (IPConverter.ip_to_int('1.1.1.0'), IPConverter.ip_to_int('1.1.1.255'),
         13335, 'CLOUDFLARE', 'IGP', 'cloudflare:1'),
        (IPConverter.ip_to_int('1.0.0.0'), IPConverter.ip_to_int('1.0.0.255'),
         13335, 'CLOUDFLARE', 'IGP', 'cloudflare:1'),
        
        # OpenDNS
        (IPConverter.ip_to_int('208.67.222.0'), IPConverter.ip_to_int('208.67.222.255'),
         8452, 'OPENDNS', 'IGP', 'opendns:65000'),
        (IPConverter.ip_to_int('208.67.220.0'), IPConverter.ip_to_int('208.67.220.255'),
         8452, 'OPENDNS', 'IGP', 'opendns:65000'),
        
        # Quad9
        (IPConverter.ip_to_int('9.9.9.0'), IPConverter.ip_to_int('9.9.9.255'),
         22652, 'QUAD9', 'IGP', 'quad9:65000'),
        
        # Level3 Communications
        (IPConverter.ip_to_int('209.244.0.0'), IPConverter.ip_to_int('209.244.0.255'),
         1, 'LEVEL3', 'IGP', 'level3:65001'),
        
        # Verizon
        (IPConverter.ip_to_int('4.0.0.0'), IPConverter.ip_to_int('4.0.0.255'),
         701, 'VERIZON', 'IGP', 'verizon:65001'),
    ]

    # AS information database
    _AS_INFO_DB = {
        15169: {'name': 'GOOGLE', 'country': 'US', 'description': 'Google Inc.'},
        13335: {'name': 'CLOUDFLARE', 'country': 'US', 'description': 'Cloudflare Inc.'},
        8452: {'name': 'OPENDNS', 'country': 'US', 'description': 'Cisco Umbrella'},
        22652: {'name': 'QUAD9', 'country': 'US', 'description': 'Quad9 Foundation'},
        1: {'name': 'LEVEL3', 'country': 'US', 'description': 'Level 3 Communications'},
        701: {'name': 'VERIZON', 'country': 'US', 'description': 'Verizon Communications'},
        3356: {'name': 'LEASEWEB', 'country': 'NL', 'description': 'LeaseWeb Global B.V.'},
        2906: {'name': 'NETFLIX', 'country': 'US', 'description': 'Netflix Inc.'},
        16509: {'name': 'AMAZON', 'country': 'US', 'description': 'Amazon.com Inc.'},
    }

    def __init__(self, prefix_table: Optional[List[Tuple]] = None,
                 as_info_db: Optional[Dict] = None):
        """
        Initialize BGP analyzer with optional custom data.
        
        Args:
            prefix_table: Custom BGP prefix table. If None, uses _SAMPLE_PREFIXES
            as_info_db: Custom AS information database. If None, uses _AS_INFO_DB
        """
        self.prefix_table = prefix_table if prefix_table is not None else self._SAMPLE_PREFIXES
        self.as_info_db = as_info_db if as_info_db is not None else self._AS_INFO_DB
        self._cache = {}

    def analyze_ip(self, ip_address: str) -> Dict:
        """
        Analyze BGP routing information for an IP address.
        
        Uses longest-prefix matching to find the origin AS and route information.
        
        Args:
            ip_address: IP address to analyze (e.g., "8.8.8.8")
            
        Returns:
            Dictionary containing:
                - ip: The queried IP address
                - asn: Autonomous System Number
                - as_name: AS name/identifier
                - route_prefix: CIDR prefix containing the IP
                - origin: Route origin (IGP, EGP, INCOMPLETE)
                - community: BGP community values
                - path: AS path (list of ASNs)
                - country: Country where AS is registered
        """
        # Check cache
        if ip_address in self._cache:
            return self._cache[ip_address].copy()

        try:
            ip_int = IPConverter.ip_to_int(ip_address)
        except Exception:
            result = {
                'ip': ip_address,
                'asn': None,
                'as_name': None,
                'route_prefix': None,
                'origin': None,
                'community': None,
                'path': [],
                'country': None,
                'error': 'Invalid IP address'
            }
            self._cache[ip_address] = result
            return result

        # Longest-prefix match
        best_match = None
        best_prefix_len = -1

        for start, end, asn, name, origin, community in self.prefix_table:
            if start <= ip_int <= end:
                prefix_len = (end - start).bit_length()
                if prefix_len > best_prefix_len:
                    best_match = (start, end, asn, name, origin, community)
                    best_prefix_len = prefix_len

        if best_match:
            start, end, asn, name, origin, community = best_match
            start_ip = IPConverter.int_to_ip(start)
            end_ip = IPConverter.int_to_ip(end)
            
            # Calculate CIDR notation
            prefix_len = 32 - (end - start).bit_length()
            cidr = f"{start_ip}/{prefix_len}"
            
            as_info = self.as_info_db.get(asn, {})
            
            result = {
                'ip': ip_address,
                'asn': asn,
                'as_name': name,
                'route_prefix': cidr,
                'origin': origin,
                'community': community,
                'path': [asn],
                'country': as_info.get('country'),
                'last_update': 'N/A'
            }
        else:
            result = {
                'ip': ip_address,
                'asn': None,
                'as_name': 'Unknown',
                'route_prefix': None,
                'origin': None,
                'community': None,
                'path': [],
                'country': None,
                'last_update': 'N/A'
            }

        self._cache[ip_address] = result
        return result

    def get_as_info(self, asn: int) -> Dict:
        """
        Get detailed information about an Autonomous System.
        
        Args:
            asn: Autonomous System Number
            
        Returns:
            Dictionary with AS information including:
                - asn: The AS number
                - name: AS name
                - country: Country of registration
                - description: AS description
        """
        info = self.as_info_db.get(asn)
        
        if info:
            return {
                'asn': asn,
                'name': info.get('name'),
                'country': info.get('country'),
                'description': info.get('description'),
                'found': True
            }
        else:
            return {
                'asn': asn,
                'name': 'Unknown',
                'country': None,
                'description': None,
                'found': False
            }

    def find_origin(self, route_prefix: str) -> Dict:
        """
        Find the origin AS for a route prefix.
        
        Args:
            route_prefix: CIDR prefix (e.g., "8.8.8.0/24")
            
        Returns:
            Dictionary with origin AS information
        """
        try:
            # Parse CIDR
            if '/' in route_prefix:
                network, prefix = route_prefix.split('/')
                prefix = int(prefix)
            else:
                network = route_prefix
                prefix = 32

            start_int = IPConverter.ip_to_int(network)
            
            # Find matching prefix
            for table_start, table_end, asn, name, origin, community in self.prefix_table:
                if table_start <= start_int <= table_end:
                    return {
                        'route_prefix': route_prefix,
                        'asn': asn,
                        'as_name': name,
                        'origin': origin,
                        'community': community,
                        'found': True
                    }
            
            return {
                'route_prefix': route_prefix,
                'asn': None,
                'as_name': None,
                'origin': None,
                'community': None,
                'found': False
            }
        except Exception as e:
            return {
                'route_prefix': route_prefix,
                'error': str(e),
                'found': False
            }

    def trace_as_path(self, ip_address: str) -> List[int]:
        """
        Trace the AS path to a destination IP.
        
        In this offline implementation, returns the AS path from the prefix table.
        In a real implementation, this would perform traceroute and BGP analysis.
        
        Args:
            ip_address: Destination IP address
            
        Returns:
            List of ASNs representing the path
        """
        analysis = self.analyze_ip(ip_address)
        return analysis.get('path', [])

    def get_all_asns(self) -> List[int]:
        """
        Get list of all ASNs in the database.
        
        Returns:
            List of unique ASN values
        """
        asns: Set[int] = set()
        for _, _, asn, _, _, _ in self.prefix_table:
            asns.add(asn)
        return sorted(list(asns))

    def get_prefixes_for_asn(self, asn: int) -> List[str]:
        """
        Get all route prefixes for a specific ASN.
        
        Args:
            asn: Autonomous System Number
            
        Returns:
            List of CIDR prefixes
        """
        prefixes = []
        for start, end, table_asn, _, _, _ in self.prefix_table:
            if table_asn == asn:
                start_ip = IPConverter.int_to_ip(start)
                end_ip = IPConverter.int_to_ip(end)
                prefix_len = 32 - (end - start).bit_length()
                prefixes.append(f"{start_ip}/{prefix_len}")
        return prefixes

    def analyze_multiple_ips(self, ips: List[str]) -> List[Dict]:
        """
        Analyze BGP information for multiple IPs.
        
        Args:
            ips: List of IP addresses
            
        Returns:
            List of analysis results
        """
        return [self.analyze_ip(ip) for ip in ips]

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()

    def get_statistics(self) -> Dict:
        """
        Get statistics about the BGP database.
        
        Returns:
            Dictionary with BGP database statistics
        """
        return {
            'total_prefixes': len(self.prefix_table),
            'total_asns': len(self.get_all_asns()),
            'cached_ips': len(self._cache),
            'as_info_entries': len(self.as_info_db)
        }
