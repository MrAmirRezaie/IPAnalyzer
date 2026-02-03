"""IP range and CIDR analysis utilities."""
from ipaddress import ip_network, ip_address
from typing import List, Dict


class IPRangeAnalyzer:
    def analyze_cidr(self, cidr: str) -> Dict:
        net = ip_network(cidr, strict=False)
        return {
            'cidr': cidr,
            'network': str(net.network_address),
            'netmask': str(net.netmask),
            'prefixlen': net.prefixlen,
            'total_addresses': net.num_addresses,
        }

    def subnet_division(self, cidr: str, new_prefix: int) -> List[str]:
        net = ip_network(cidr, strict=False)
        subs = list(net.subnets(new_prefix=new_prefix))
        return [str(s) for s in subs]

    def ip_in_range(self, ip: str, cidr: str) -> bool:
        try:
            return ip_address(ip) in ip_network(cidr, strict=False)
        except Exception:
            return False

    def overlap(self, cidr1: str, cidr2: str) -> bool:
        n1 = ip_network(cidr1, strict=False)
        n2 = ip_network(cidr2, strict=False)
        return n1.overlaps(n2)
"""
IP Range Analyzer Module
Analyze IP ranges, CIDR notation, and subnets
"""

from typing import List, Dict, Tuple
from .ip_utils import CIDRCalculator, IPConverter, IPValidator


class IPRangeAnalyzer:
    """Analyze IP ranges and subnets"""
    
    def __init__(self):
        """Initialize IP Range Analyzer"""
        pass
    
    def analyze_cidr(self, cidr: str) -> Dict:
        """Analyze CIDR block in detail"""
        if not IPValidator.is_valid_cidr(cidr):
            raise ValueError(f"Invalid CIDR: {cidr}")
        
        network_ip, broadcast_ip, netmask, prefix = CIDRCalculator.parse_cidr(cidr)
        start_int, end_int = CIDRCalculator.get_ip_range(cidr)
        
        total_hosts = end_int - start_int + 1
        usable_hosts = max(0, total_hosts - 2)  # Exclude network and broadcast
        
        return {
            'cidr': cidr,
            'network_ip': network_ip,
            'broadcast_ip': broadcast_ip,
            'netmask': netmask,
            'prefix_length': prefix,
            'total_addresses': total_hosts,
            'usable_hosts': usable_hosts,
            'ip_class': self.get_ip_class(network_ip),
            'first_usable': IPConverter.int_to_ip(start_int + 1) if usable_hosts > 0 else network_ip,
            'last_usable': IPConverter.int_to_ip(end_int - 1) if usable_hosts > 0 else broadcast_ip,
        }
    
    def get_ip_class(self, ip: str) -> str:
        """Classify IP into Class A, B, C, D, E"""
        first_octet = int(ip.split('.')[0])
        
        if first_octet < 128:
            return 'Class A'
        elif first_octet < 192:
            return 'Class B'
        elif first_octet < 224:
            return 'Class C'
        elif first_octet < 240:
            return 'Class D (Multicast)'
        else:
            return 'Class E (Reserved)'
    
    def get_subnet_mask_from_prefix(self, prefix: int) -> str:
        """Convert prefix length to subnet mask"""
        if not (0 <= prefix <= 32):
            raise ValueError(f"Invalid prefix length: {prefix}")
        
        mask_bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        return IPConverter.int_to_ip(mask_bits)
    
    def get_prefix_from_subnet_mask(self, mask: str) -> int:
        """Convert subnet mask to prefix length"""
        if not IPValidator.is_valid_ipv4(mask):
            raise ValueError(f"Invalid subnet mask: {mask}")
        
        mask_int = IPConverter.ip_to_int(mask)
        # Count leading ones
        prefix = 0
        for i in range(32):
            if mask_int & (1 << (31 - i)):
                prefix += 1
            else:
                break
        return prefix
    
    def supernet(self, cidrs: List[str]) -> str:
        """Find supernet (smallest network containing all given networks)"""
        if not cidrs:
            raise ValueError("Empty CIDR list")
        
        if len(cidrs) == 1:
            return cidrs[0]
        
        # Get all starting IPs and their prefixes
        ips_and_prefixes = []
        for cidr in cidrs:
            network_ip, _, _, prefix = CIDRCalculator.parse_cidr(cidr)
            ips_and_prefixes.append((IPConverter.ip_to_int(network_ip), prefix))
        
        # Start with the smallest prefix (largest network)
        min_prefix = min(p[1] for p in ips_and_prefixes)
        
        # Find common prefix
        for new_prefix in range(min_prefix, -1, -1):
            mask = (0xFFFFFFFF << (32 - new_prefix)) & 0xFFFFFFFF
            
            # Check if all IPs match under this mask
            first_masked = ips_and_prefixes[0][0] & mask
            all_match = all((ip & mask) == first_masked for ip, _ in ips_and_prefixes)
            
            if all_match:
                supernet_ip = IPConverter.int_to_ip(first_masked)
                return f"{supernet_ip}/{new_prefix}"
        
        return "0.0.0.0/0"
    
    def summarize_ranges(self, cidr_list: List[str]) -> List[str]:
        """Summarize multiple overlapping CIDR blocks"""
        if not cidr_list:
            return []
        
        # Simple approach: find supernet
        try:
            return [self.supernet(cidr_list)]
        except:
            return cidr_list
    
    def subnet_division(self, cidr: str, new_prefix: int) -> List[str]:
        """Divide CIDR into smaller subnets"""
        if not IPValidator.is_valid_cidr(cidr):
            raise ValueError(f"Invalid CIDR: {cidr}")
        
        _, _, _, original_prefix = CIDRCalculator.parse_cidr(cidr)
        
        if new_prefix <= original_prefix:
            return [cidr]
        
        return CIDRCalculator.subnets_from_cidr(cidr, new_prefix)
    
    def ip_in_range(self, ip: str, cidr: str) -> bool:
        """Check if IP is in given CIDR range"""
        if not IPValidator.is_valid_ipv4(ip):
            raise ValueError(f"Invalid IP: {ip}")
        if not IPValidator.is_valid_cidr(cidr):
            raise ValueError(f"Invalid CIDR: {cidr}")
        
        ip_int = IPConverter.ip_to_int(ip)
        start_int, end_int = CIDRCalculator.get_ip_range(cidr)
        
        return start_int <= ip_int <= end_int
    
    def find_overlaps(self, cidr1: str, cidr2: str) -> bool:
        """Check if two CIDR blocks overlap"""
        start1, end1 = CIDRCalculator.get_ip_range(cidr1)
        start2, end2 = CIDRCalculator.get_ip_range(cidr2)
        
        return not (end1 < start2 or end2 < start1)
    
    def generate_ip_list(self, cidr: str, limit: int = 1000) -> List[str]:
        """Generate list of IPs in CIDR (with limit)"""
        ips = CIDRCalculator.get_usable_ips(cidr)
        return ips[:limit]
    
    def analyze_multiple_ranges(self, cidrs: List[str]) -> Dict:
        """Analyze multiple IP ranges together"""
        analyses = []
        total_ips = 0
        
        for cidr in cidrs:
            analysis = self.analyze_cidr(cidr)
            analyses.append(analysis)
            total_ips += analysis['total_addresses']
        
        return {
            'ranges': analyses,
            'total_ranges': len(cidrs),
            'total_addresses': total_ips,
            'supernet': self.supernet(cidrs),
            'overlaps': self._check_all_overlaps(cidrs)
        }
    
    def _check_all_overlaps(self, cidrs: List[str]) -> List[Dict]:
        """Find all overlaps between CIDR blocks"""
        overlaps = []
        for i in range(len(cidrs)):
            for j in range(i + 1, len(cidrs)):
                if self.find_overlaps(cidrs[i], cidrs[j]):
                    overlaps.append({
                        'cidr1': cidrs[i],
                        'cidr2': cidrs[j]
                    })
        return overlaps
