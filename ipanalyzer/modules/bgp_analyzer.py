"""Minimal BGP analyzer using an offline prefix-to-AS sample table."""
from typing import Dict, List
from ipanalyzer.modules.ip_utils import IPConverter


class BGPAnalyzer:
    """Lightweight BGP analyzer for offline use.

    This module performs a longest-prefix match against a small
    prefix table to find the origin ASN and basic info.
    """

    # Sample prefix table: (start_int, end_int, asn, as_name)
    _SAMPLE_PREFIXES = [
        (IPConverter.ip_to_int('8.8.8.0'), IPConverter.ip_to_int('8.8.8.255'), 15169, 'GOOGLE'),
        (IPConverter.ip_to_int('1.1.1.0'), IPConverter.ip_to_int('1.1.1.255'), 13335, 'CLOUDFLARE'),
    ]

    def __init__(self, prefix_table: List = None):
        self.prefix_table = prefix_table if prefix_table is not None else self._SAMPLE_PREFIXES

    def analyze_ip(self, ip_address: str) -> Dict:
        ip_int = IPConverter.ip_to_int(ip_address)
        best = None
        for start, end, asn, name in self.prefix_table:
            if start <= ip_int <= end:
                # pick any matching; table is small
                best = {'ip': ip_address, 'asn': asn, 'as_name': name, 'route_prefix': f"{IPConverter.int_to_ip(start)}/{32 - (end - start).bit_length()}", 'path': [asn]}
                break
        if best:
            return best
        return {'ip': ip_address, 'asn': None, 'as_name': None, 'route_prefix': None, 'path': []}

    def get_as_info(self, asn: int) -> Dict:
        # Minimal stub: return name if present
        for _, _, a, name in self.prefix_table:
            if a == asn:
                return {'asn': asn, 'name': name}
        return {'asn': asn, 'name': None}
