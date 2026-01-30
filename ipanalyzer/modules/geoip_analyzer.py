"""GeoIP Analyzer - simple offline GeoIP lookup using in-memory ranges
"""
from typing import List, Dict
import math
from ipanalyzer.modules.ip_utils import IPConverter


class GeoIPAnalyzer:
    """Minimal GeoIP analyzer using a small offline table.

    This implementation is intentionally lightweight and uses an
    in-memory list of (start_int, end_int, metadata) entries. For
    production use replace with a proper GeoLite2 parser.
    """

    # Sample in-memory DB: tuples of (start_int, end_int, metadata)
    _SAMPLE_DB = [
        # 8.8.8.0/24 - Google
        (IPConverter.ip_to_int("8.8.8.0"), IPConverter.ip_to_int("8.8.8.255"), {
            'country': 'United States', 'country_code': 'US', 'city': 'Mountain View',
            'latitude': 37.386, 'longitude': -122.0838, 'timezone': 'America/Los_Angeles',
            'isp': 'Google LLC', 'organization': 'Google'
        }),
        # 1.1.1.0/24 - Cloudflare
        (IPConverter.ip_to_int("1.1.1.0"), IPConverter.ip_to_int("1.1.1.255"), {
            'country': 'Australia', 'country_code': 'AU', 'city': 'Sydney',
            'latitude': -33.8591, 'longitude': 151.2002, 'timezone': 'Australia/Sydney',
            'isp': 'Cloudflare, Inc.', 'organization': 'Cloudflare'
        }),
    ]

    def __init__(self, db: List = None):
        self.db = db if db is not None else self._SAMPLE_DB

    def analyze(self, ip_address: str) -> Dict:
        ip_int = IPConverter.ip_to_int(ip_address)
        for start, end, meta in self.db:
            if start <= ip_int <= end:
                result = meta.copy()
                result.update({'ip': ip_address})
                return result
        return {'ip': ip_address, 'country': 'Unknown', 'country_code': None}

    def batch_analyze(self, ips: List[str]) -> List[Dict]:
        return [self.analyze(ip) for ip in ips]

    @staticmethod
    def calculate_distance(ip1_meta: Dict, ip2_meta: Dict) -> float:
        """Calculate approximate distance (km) between two metadata entries.

        Accepts dicts with 'latitude' and 'longitude'. Returns kilometers as float.
        """
        try:
            lat1 = float(ip1_meta['latitude'])
            lon1 = float(ip1_meta['longitude'])
            lat2 = float(ip2_meta['latitude'])
            lon2 = float(ip2_meta['longitude'])
        except Exception:
            return -1.0

        # Haversine formula
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
