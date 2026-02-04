"""BGP Analyzer

Provides a lightweight BGP analyzer with simple ASN lookup and a small
offline prefix table. Includes compatibility method `get_asn_for_ip` used
by older tests and callers.
"""
from typing import Dict, List, Optional, Tuple, Set
import ipaddress


class BGPAnalyzer:
    # Small sample prefix table: (start_int, end_int, asn, name)
    _SAMPLE_PREFIXES: List[Tuple[int, int, int, str]] = [
        (int(ipaddress.ip_address('8.8.8.0')), int(ipaddress.ip_address('8.8.8.255')), 15169, 'GOOGLE'),
        (int(ipaddress.ip_address('1.1.1.0')), int(ipaddress.ip_address('1.1.1.255')), 13335, 'CLOUDFLARE'),
        (int(ipaddress.ip_address('9.9.9.0')), int(ipaddress.ip_address('9.9.9.255')), 22652, 'QUAD9'),
    ]

    _AS_INFO_DB = {
        15169: {'name': 'GOOGLE', 'country': 'US'},
        13335: {'name': 'CLOUDFLARE', 'country': 'US'},
        22652: {'name': 'QUAD9', 'country': 'US'},
    }

    def __init__(self, prefixes: Optional[List[Tuple]] = None):
        self.prefixes = prefixes if prefixes is not None else self._SAMPLE_PREFIXES
        self._cache: Dict[str, Dict] = {}

    def analyze_ip(self, ip: str) -> Dict:
        if ip in self._cache:
            return self._cache[ip].copy()
        try:
            ipa = ipaddress.ip_address(ip)
            ip_int = int(ipa)
        except Exception:
            return {'ip': ip, 'asn': None, 'error': 'invalid_ip'}

        # find the prefix containing the ip (first match is fine for small table)
        for start, end, asn, name in self.prefixes:
            if start <= ip_int <= end:
                res = {'ip': ip, 'asn': f'AS{asn}', 'name': name, 'country': self._AS_INFO_DB.get(asn, {}).get('country')}
                self._cache[ip] = res
                return res

        res = {'ip': ip, 'asn': None, 'name': None}
        self._cache[ip] = res
        return res

    def get_asn_for_ip(self, ip: str) -> Dict:
        r = self.analyze_ip(ip)
        # keep old return shape for compatibility
        return {'ip': ip, 'asn': r.get('asn'), 'description': r.get('name')}

    def get_as_info(self, asn: int) -> Dict:
        """Return information for an ASN from the local AS DB.

        Returns a dict with keys: asn, name, country, found
        """
        info = self._AS_INFO_DB.get(asn)
        if info:
            return {
                'asn': asn,
                'name': info.get('name'),
                'country': info.get('country'),
                'found': True
            }
        return {
            'asn': asn,
            'name': None,
            'country': None,
            'found': False
        }

    def find_origin(self, route_prefix: str) -> Dict:
        """Find the origin AS for a CIDR prefix (offline lookup)."""
        try:
            network = ipaddress.ip_network(route_prefix, strict=False)
        except Exception as e:
            return {'route_prefix': route_prefix, 'error': str(e), 'found': False}

        net_start = int(network.network_address)
        net_end = int(network.broadcast_address)

        for start, end, asn, name in self.prefixes:
            # match if network overlaps stored prefix range
            if start <= net_start <= end or start <= net_end <= end:
                return {'route_prefix': route_prefix, 'asn': asn, 'as_name': name, 'found': True}

        return {'route_prefix': route_prefix, 'asn': None, 'as_name': None, 'found': False}

    def trace_as_path(self, ip_address: str) -> List[int]:
        """Return a minimal AS path for the given IP (offline approximation)."""
        r = self.analyze_ip(ip_address)
        asn_str = r.get('asn')
        if asn_str and isinstance(asn_str, str) and asn_str.upper().startswith('AS'):
            try:
                return [int(asn_str[2:])]
            except ValueError:
                return []
        return []

    def get_all_asns(self) -> List[int]:
        """Return a sorted list of unique ASNs from the prefix table."""
        asns: Set[int] = set()
        for _, _, asn, _ in self.prefixes:
            asns.add(asn)
        return sorted(asns)

    def get_prefixes_for_asn(self, asn: int) -> List[str]:
        """Return a list of CIDR prefixes associated with an ASN."""
        cidrs: List[str] = []
        for start, end, table_asn, _ in self.prefixes:
            if table_asn != asn:
                continue
            start_ip = ipaddress.ip_address(start)
            end_ip = ipaddress.ip_address(end)
            networks = ipaddress.summarize_address_range(start_ip, end_ip)
            cidrs.extend(str(n) for n in networks)
        return cidrs

    def analyze_multiple_ips(self, ips: List[str]) -> List[Dict]:
        return [self.analyze_ip(ip) for ip in ips]

    def clear_cache(self) -> None:
        self._cache.clear()

    def get_statistics(self) -> Dict:
        return {
            'total_prefixes': len(self.prefixes),
            'total_asns': len(self.get_all_asns()),
            'cached_ips': len(self._cache),
            'as_info_entries': len(self._AS_INFO_DB)
        }
