"""GeoIP Analyzer - simple, reliable implementation.

Provides an offline GeoIP lookup using a small CSV shipped with the
package or an in-memory fallback. Offers `lookup`/`analyze`, batch
lookup, distance calculation and a simple cache.
"""

from typing import List, Dict, Optional, Tuple
import ipaddress
from pathlib import Path
import csv
import math


def _ip_to_int(ip: str) -> int:
    return int(ipaddress.ip_address(ip))


class GeoIPAnalyzer:
    _SAMPLE_DB: List[Tuple[int, int, Dict]] = [
        (
            _ip_to_int("8.8.8.0"),
            _ip_to_int("8.8.8.255"),
            {
                "country": "United States",
                "country_code": "US",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.0838,
                "timezone": "America/Los_Angeles",
                "isp": "Google LLC",
                "organization": "Google",
                "asn": 15169,
            },
        ),
        (
            _ip_to_int("1.1.1.0"),
            _ip_to_int("1.1.1.255"),
            {
                "country": "Australia",
                "country_code": "AU",
                "city": "Sydney",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "timezone": "Australia/Sydney",
                "isp": "Cloudflare",
                "organization": "Cloudflare",
                "asn": 13335,
            },
        ),
    ]

    def __init__(self, db: Optional[List[Tuple[int, int, Dict]]] = None):
        csv_path = Path(__file__).resolve().parents[1] / "data" / "geoip_db.csv"
        if db is not None:
            self.db = db
        elif csv_path.exists():
            rows: List[Tuple[int, int, Dict]] = []
            try:
                with open(csv_path, newline="", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for r in reader:
                        try:
                            net = ipaddress.ip_network(r["network"])
                            start = int(net.network_address)
                            # IPv6 doesn't have broadcast_address attribute
                            end = int(getattr(net, "broadcast_address", list(net)[-1]))
                            meta = {
                                "country": r.get("country"),
                                "country_code": r.get("country_code"),
                                "city": r.get("city"),
                                "latitude": float(r.get("latitude")) if r.get("latitude") else None,
                                "longitude": float(r.get("longitude")) if r.get("longitude") else None,
                                "timezone": r.get("timezone"),
                                "isp": r.get("isp"),
                                "organization": r.get("organization"),
                                "asn": int(r.get("asn")) if r.get("asn") else None,
                            }
                            rows.append((start, end, meta))
                        except Exception:
                            continue
            except Exception:
                rows = []
            self.db = rows if rows else list(self._SAMPLE_DB)
        else:
            self.db = list(self._SAMPLE_DB)

        self._cache: Dict[str, Dict] = {}

    def _find(self, ip: str) -> Dict:
        if ip in self._cache:
            return self._cache[ip].copy()
        try:
            ipa = ipaddress.ip_address(ip)
            ip_int = int(ipa)
        except Exception:
            res = {"ip": ip, "error": "invalid_ip"}
            self._cache[ip] = res
            return res

        for start, end, meta in self.db:
            if start <= ip_int <= end:
                out = meta.copy()
                out["ip"] = ip
                self._cache[ip] = out
                return out

        out = {"ip": ip, "country": None, "country_code": None, "city": None, "latitude": None, "longitude": None,
               "timezone": None, "isp": None, "organization": None, "asn": None}
        self._cache[ip] = out
        return out

    # public API
    def lookup(self, ip: str) -> Dict:
        return self._find(ip)

    def analyze(self, ip: str) -> Dict:
        return self.lookup(ip)

    def batch_lookup(self, ips: List[str]) -> List[Dict]:
        return [self.lookup(i) for i in ips]

    def clear_cache(self) -> None:
        self._cache.clear()

    def analyze_with_distance(self, ip_address: str, reference_ip: str) -> Dict:
        result = self.analyze(ip_address)
        reference = self.analyze(reference_ip)
        distance = self.calculate_distance(result, reference)
        result["distance_to_reference"] = distance
        result["reference_ip"] = reference_ip
        return result

    @staticmethod
    def calculate_distance(geo1: Dict, geo2: Dict) -> float:
        try:
            lat1 = geo1.get("latitude")
            lon1 = geo1.get("longitude")
            lat2 = geo2.get("latitude")
            lon2 = geo2.get("longitude")
            if None in (lat1, lon1, lat2, lon2):
                return -1.0
            lat1 = float(lat1)
            lon1 = float(lon1)
            lat2 = float(lat2)
            lon2 = float(lon2)
        except (TypeError, ValueError, KeyError):
            return -1.0

        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_countries_distribution(self, ips: List[str]) -> Dict[str, int]:
        distribution: Dict[str, int] = {}
        for ip in ips:
            result = self.analyze(ip)
            country_code = result.get("country_code") or "XX"
            distribution[country_code] = distribution.get(country_code, 0) + 1
        return distribution

    def find_ips_in_country(self, country_code: str) -> List[Tuple[str, str]]:
        ranges: List[Tuple[str, str]] = []
        for start_int, end_int, meta in self.db:
            if meta.get("country_code") == country_code:
                start_ip = str(ipaddress.ip_address(start_int))
                end_ip = str(ipaddress.ip_address(end_int))
                ranges.append((start_ip, end_ip))
        return ranges

    def get_cache_stats(self) -> Dict:
        return {"cached_ips": len(self._cache), "cache_size_kb": len(str(self._cache)) // 1024, "db_entries": len(self.db)}

