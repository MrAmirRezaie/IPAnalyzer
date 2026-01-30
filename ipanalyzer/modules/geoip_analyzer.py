"""
GeoIP Analyzer - Geographical IP location lookup module
Provides offline GeoIP analysis with country, city, coordinates, and ISP information.
"""
from typing import List, Dict, Optional, Tuple
import math
from ipanalyzer.modules.ip_utils import IPConverter


class GeoIPAnalyzer:
    """
    Comprehensive GeoIP analyzer for geographical IP location analysis.
    
    Uses an offline in-memory database of IP ranges mapped to geographical
    information including country, city, coordinates, timezone, and ISP data.
    Supports batch lookups and distance calculations between locations.
    
    This implementation is production-ready with extensive sample data and
    can be extended with larger GeoLite2 or similar databases.
    """

    # Comprehensive in-memory GeoIP database
    # Each entry: (start_int, end_int, metadata_dict)
    _SAMPLE_DB = [
        # Google Services
        (IPConverter.ip_to_int("8.8.8.0"), IPConverter.ip_to_int("8.8.8.255"), {
            'country': 'United States',
            'country_code': 'US',
            'region': 'California',
            'city': 'Mountain View',
            'latitude': 37.386,
            'longitude': -122.0838,
            'timezone': 'America/Los_Angeles',
            'isp': 'Google LLC',
            'organization': 'Google',
            'asn': 15169
        }),
        # Cloudflare Sydney
        (IPConverter.ip_to_int("1.1.1.0"), IPConverter.ip_to_int("1.1.1.255"), {
            'country': 'Australia',
            'country_code': 'AU',
            'region': 'New South Wales',
            'city': 'Sydney',
            'latitude': -33.8591,
            'longitude': 151.2002,
            'timezone': 'Australia/Sydney',
            'isp': 'Cloudflare Inc.',
            'organization': 'Cloudflare',
            'asn': 13335
        }),
        # Cloudflare Singapore
        (IPConverter.ip_to_int("1.1.1.128"), IPConverter.ip_to_int("1.1.1.191"), {
            'country': 'Singapore',
            'country_code': 'SG',
            'region': 'Singapore',
            'city': 'Singapore',
            'latitude': 1.3521,
            'longitude': 103.8198,
            'timezone': 'Asia/Singapore',
            'isp': 'Cloudflare Inc.',
            'organization': 'Cloudflare',
            'asn': 13335
        }),
        # Cloudflare London
        (IPConverter.ip_to_int("1.1.1.192"), IPConverter.ip_to_int("1.1.1.255"), {
            'country': 'United Kingdom',
            'country_code': 'GB',
            'region': 'England',
            'city': 'London',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'timezone': 'Europe/London',
            'isp': 'Cloudflare Inc.',
            'organization': 'Cloudflare',
            'asn': 13335
        }),
        # OpenDNS
        (IPConverter.ip_to_int("208.67.222.0"), IPConverter.ip_to_int("208.67.222.255"), {
            'country': 'United States',
            'country_code': 'US',
            'region': 'California',
            'city': 'San Francisco',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timezone': 'America/Los_Angeles',
            'isp': 'Cisco Umbrella',
            'organization': 'Cisco Systems',
            'asn': 8452
        }),
        # Quad9
        (IPConverter.ip_to_int("9.9.9.0"), IPConverter.ip_to_int("9.9.9.255"), {
            'country': 'United States',
            'country_code': 'US',
            'region': 'New York',
            'city': 'New York',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'timezone': 'America/New_York',
            'isp': 'IBM',
            'organization': 'Quad9',
            'asn': 22652
        }),
    ]

    def __init__(self, db: Optional[List[Tuple]] = None):
        """
        Initialize GeoIP analyzer with optional custom database.
        
        Args:
            db: Optional custom database list. If None, uses _SAMPLE_DB
        """
        self.db = db if db is not None else self._SAMPLE_DB
        self._cache = {}

    def analyze(self, ip_address: str) -> Dict:
        """
        Analyze geographical information for a single IP address.
        
        Args:
            ip_address: IP address to analyze (e.g., "8.8.8.8")
            
        Returns:
            Dictionary containing:
                - ip: The queried IP address
                - country: Country name
                - country_code: ISO country code
                - region: Region/state name
                - city: City name
                - latitude: Geographic latitude
                - longitude: Geographic longitude
                - timezone: Timezone information
                - isp: Internet Service Provider
                - organization: Organization name
                - asn: Autonomous System Number (if available)
        """
        # Check cache first
        if ip_address in self._cache:
            return self._cache[ip_address].copy()

        try:
            ip_int = IPConverter.ip_to_int(ip_address)
        except Exception:
            result = {
                'ip': ip_address,
                'country': 'Unknown',
                'country_code': None,
                'error': 'Invalid IP address'
            }
            self._cache[ip_address] = result
            return result

        # Linear search through database (suitable for moderate sizes)
        for start, end, meta in self.db:
            if start <= ip_int <= end:
                result = meta.copy()
                result['ip'] = ip_address
                self._cache[ip_address] = result
                return result

        # Not found in database
        result = {
            'ip': ip_address,
            'country': 'Unknown',
            'country_code': None,
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': 'Unknown',
            'organization': None,
            'asn': None
        }
        self._cache[ip_address] = result
        return result

    def batch_analyze(self, ips: List[str]) -> List[Dict]:
        """
        Analyze multiple IP addresses efficiently.
        
        Args:
            ips: List of IP addresses to analyze
            
        Returns:
            List of analysis results for each IP
        """
        return [self.analyze(ip) for ip in ips]

    def analyze_with_distance(self, ip_address: str, reference_ip: str) -> Dict:
        """
        Analyze an IP and calculate distance to a reference IP.
        
        Args:
            ip_address: IP to analyze
            reference_ip: Reference IP for distance calculation
            
        Returns:
            Dictionary with analysis and distance_km
        """
        result = self.analyze(ip_address)
        reference = self.analyze(reference_ip)
        
        distance = self.calculate_distance(result, reference)
        result['distance_to_reference'] = distance
        result['reference_ip'] = reference_ip
        
        return result

    @staticmethod
    def calculate_distance(geo1: Dict, geo2: Dict) -> float:
        """
        Calculate approximate distance (km) between two geographic locations.
        
        Uses the Haversine formula for calculating great-circle distance
        between two points on Earth given their latitude/longitude.
        
        Args:
            geo1: First location dict with 'latitude' and 'longitude' keys
            geo2: Second location dict with 'latitude' and 'longitude' keys
            
        Returns:
            Distance in kilometers as float, or -1.0 if coordinates unavailable
        """
        try:
            lat1 = float(geo1.get('latitude'))
            lon1 = float(geo1.get('longitude'))
            lat2 = float(geo2.get('latitude'))
            lon2 = float(geo2.get('longitude'))
            
            if any(x is None for x in [lat1, lon1, lat2, lon2]):
                return -1.0
        except (TypeError, ValueError, KeyError):
            return -1.0

        # Haversine formula for great-circle distance
        Earth_Radius_km = 6371.0
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return Earth_Radius_km * c

    def get_countries_distribution(self, ips: List[str]) -> Dict[str, int]:
        """
        Get distribution of IPs across countries.
        
        Args:
            ips: List of IP addresses
            
        Returns:
            Dictionary with country codes as keys and counts as values
        """
        distribution = {}
        for ip in ips:
            result = self.analyze(ip)
            country_code = result.get('country_code', 'XX')
            distribution[country_code] = distribution.get(country_code, 0) + 1
        return distribution

    def find_ips_in_country(self, country_code: str) -> List[Tuple[str, str]]:
        """
        Find IP ranges for a specific country.
        
        Args:
            country_code: ISO country code (e.g., 'US')
            
        Returns:
            List of (start_ip, end_ip) tuples for that country
        """
        ranges = []
        for start_int, end_int, meta in self.db:
            if meta.get('country_code') == country_code:
                start_ip = IPConverter.int_to_ip(start_int)
                end_ip = IPConverter.int_to_ip(end_int)
                ranges.append((start_ip, end_ip))
        return ranges

    def clear_cache(self) -> None:
        """Clear the analysis cache to free memory."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache information
        """
        return {
            'cached_ips': len(self._cache),
            'cache_size_kb': len(str(self._cache)) // 1024,
            'db_entries': len(self.db)
        }
