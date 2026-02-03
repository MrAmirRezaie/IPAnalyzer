"""Bulk DNS processor using threads from the standard library."""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict


class DNSBulkProcessor:
    def __init__(self, workers: int = 10):
        self.workers = workers

    def resolve(self, host: str) -> Dict:
        result = {'host': host}
        try:
            infos = socket.getaddrinfo(host, None)
            addrs = sorted({ai[4][0] for ai in infos})
            result['addresses'] = addrs
        except Exception as e:
            result['error'] = str(e)
        return result

    def reverse(self, ip: str) -> Dict:
        result = {'ip': ip}
        try:
            name = socket.gethostbyaddr(ip)[0]
            result['name'] = name
        except Exception as e:
            result['error'] = str(e)
        return result

    def bulk_resolve(self, hosts: List[str]) -> List[Dict]:
        out = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futures = {ex.submit(self.resolve, h): h for h in hosts}
            for fut in as_completed(futures):
                out.append(fut.result())
        return out

    def bulk_reverse(self, ips: List[str]) -> List[Dict]:
        out = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futures = {ex.submit(self.reverse, ip): ip for ip in ips}
            for fut in as_completed(futures):
                out.append(fut.result())
        return out
"""
DNS Bulk Processor - Multi-threaded DNS lookup and resolution module
Provides batch forward and reverse DNS processing with caching and export capabilities.
"""
from typing import List, Dict, Optional
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class DNSBulkProcessor:
    """
    High-performance DNS bulk processing with multi-threading.
    
    Performs concurrent forward DNS lookups (hostname to IP) and reverse
    DNS resolution (IP to hostname) with configurable thread pools, timeouts,
    and caching. Supports batch processing from files and various export formats.
    """

    def __init__(self, threads: int = 8, timeout: int = 5):
        """
        Initialize DNS bulk processor.
        
        Args:
            threads: Number of concurrent threads (default: 8)
            timeout: DNS query timeout in seconds (default: 5)
        """
        self.threads = max(1, min(int(threads), 32))  # Limit threads to reasonable range
        self.timeout = max(1, int(timeout))
        self._cache = {}
        self._stats = {'forward': 0, 'reverse': 0, 'cached': 0, 'errors': 0}
        
        # Set socket timeout globally
        socket.setdefaulttimeout(self.timeout)

    def _forward(self, hostname: str) -> Dict:
        """
        Perform forward DNS lookup (hostname to IPs).
        
        Args:
            hostname: Hostname to resolve
            
        Returns:
            Dictionary with hostname, ips list, and error info
        """
        cache_key = f"forward:{hostname}"
        if cache_key in self._cache:
            self._stats['cached'] += 1
            return self._cache[cache_key].copy()

        try:
            infos = socket.getaddrinfo(hostname, None)
            ips = sorted({item[4][0] for item in infos})
            result = {'hostname': hostname, 'ips': ips, 'error': None}
            self._cache[cache_key] = result
            self._stats['forward'] += 1
            return result.copy()
        except socket.timeout:
            result = {'hostname': hostname, 'ips': [], 'error': 'timeout'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()
        except socket.gaierror as e:
            result = {'hostname': hostname, 'ips': [], 'error': f'gaierror: {str(e)}'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()
        except Exception as e:
            result = {'hostname': hostname, 'ips': [], 'error': f'error: {str(e)}'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()

    def _reverse(self, ip: str) -> Dict:
        """
        Perform reverse DNS lookup (IP to hostname).
        
        Args:
            ip: IP address to resolve
            
        Returns:
            Dictionary with ip, hostname, and error info
        """
        cache_key = f"reverse:{ip}"
        if cache_key in self._cache:
            self._stats['cached'] += 1
            return self._cache[cache_key].copy()

        try:
            name = socket.gethostbyaddr(ip)[0]
            result = {'ip': ip, 'hostname': name, 'error': None}
            self._cache[cache_key] = result
            self._stats['reverse'] += 1
            return result.copy()
        except socket.timeout:
            result = {'ip': ip, 'hostname': None, 'error': 'timeout'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()
        except socket.herror:
            result = {'ip': ip, 'hostname': None, 'error': 'not_found'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()
        except Exception as e:
            result = {'ip': ip, 'hostname': None, 'error': f'error: {str(e)}'}
            self._cache[cache_key] = result
            self._stats['errors'] += 1
            return result.copy()

    def forward_lookup_batch(self, hostnames: List[str]) -> Dict[str, Dict]:
        """
        Perform batch forward DNS lookups with multi-threading.
        
        Args:
            hostnames: List of hostnames to resolve
            
        Returns:
            Dictionary mapping hostname to result dict with ips and error
        """
        results = {}
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self._forward, h): h for h in hostnames}
            for future in as_completed(futures):
                result = future.result()
                results[result['hostname']] = result
        return results

    def reverse_lookup_batch(self, ips: List[str]) -> Dict[str, Dict]:
        """
        Perform batch reverse DNS lookups with multi-threading.
        
        Args:
            ips: List of IP addresses to resolve
            
        Returns:
            Dictionary mapping IP to result dict with hostname and error
        """
        results = {}
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self._reverse, ip): ip for ip in ips}
            for future in as_completed(futures):
                result = future.result()
                results[result.get('ip')] = result
        return results

    def batch_from_file(self, filepath: str, reverse: bool = False) -> Dict:
        """
        Load batch from file and process DNS lookups.
        
        File format: One entry per line, empty lines and lines starting
        with '#' are ignored.
        
        Args:
            filepath: Path to file with hostnames or IPs
            reverse: If True, perform reverse lookup; if False, forward lookup
            
        Returns:
            Dictionary of results
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f
                        if line.strip() and not line.strip().startswith('#')]
            
            if reverse:
                return self.reverse_lookup_batch(lines)
            else:
                return self.forward_lookup_batch(lines)
        except IOError as e:
            return {'error': f'File error: {str(e)}'}

    def export_results(self, results: Dict, format: str = 'csv') -> str:
        """
        Export DNS lookup results to various formats.
        
        Supported formats:
            - 'csv': Comma-separated values
            - 'json': JSON format (requires json module)
            - 'txt': Plain text format
        
        Args:
            results: Results dictionary from lookup operations
            format: Export format ('csv', 'json', or 'txt')
            
        Returns:
            Formatted string representation of results
        """
        if format == 'csv':
            lines = ['Source,Target,Error']
            for key, val in results.items():
                if 'hostname' in val:  # Forward lookup
                    hostname = val.get('hostname', '')
                    ips = ';'.join(val.get('ips', []))
                    error = val.get('error') or ''
                    lines.append(f'"{hostname}","{ips}","{error}"')
                else:  # Reverse lookup
                    ip = val.get('ip', '')
                    hostname = val.get('hostname') or ''
                    error = val.get('error') or ''
                    lines.append(f'"{ip}","{hostname}","{error}"')
            return '\n'.join(lines)
        
        elif format == 'json':
            import json
            return json.dumps(results, indent=2, default=str)
        
        elif format == 'txt':
            lines = []
            for key, val in results.items():
                if 'hostname' in val:  # Forward lookup
                    hostname = val.get('hostname', 'Unknown')
                    ips = ', '.join(val.get('ips', []))
                    error = val.get('error')
                    lines.append(f"Forward Lookup: {hostname}")
                    lines.append(f"  IPs: {ips}")
                    if error:
                        lines.append(f"  Error: {error}")
                else:  # Reverse lookup
                    ip = val.get('ip', 'Unknown')
                    hostname = val.get('hostname') or 'Not Found'
                    error = val.get('error')
                    lines.append(f"Reverse Lookup: {ip}")
                    lines.append(f"  Hostname: {hostname}")
                    if error:
                        lines.append(f"  Error: {error}")
                lines.append('')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f'Unsupported export format: {format}')

    def bulk_lookup(self, entries: List[str], reverse: bool = False,
                   max_batch: int = 100) -> List[Dict]:
        """
        Perform bulk lookups with automatic batching.
        
        Args:
            entries: List of hostnames or IPs
            reverse: If True, perform reverse lookup
            max_batch: Maximum entries per batch
            
        Returns:
            List of result dictionaries
        """
        results = []
        for i in range(0, len(entries), max_batch):
            batch = entries[i:i + max_batch]
            if reverse:
                batch_results = self.reverse_lookup_batch(batch)
            else:
                batch_results = self.forward_lookup_batch(batch)
            results.extend(batch_results.values())
            time.sleep(0.1)  # Small delay between batches
        return results

    def clear_cache(self) -> None:
        """Clear the DNS query cache."""
        self._cache.clear()

    def get_statistics(self) -> Dict:
        """
        Get DNS processor statistics.
        
        Returns:
            Dictionary with lookup statistics
        """
        return {
            'forward_lookups': self._stats['forward'],
            'reverse_lookups': self._stats['reverse'],
            'cached_hits': self._stats['cached'],
            'errors': self._stats['errors'],
            'cache_size': len(self._cache),
            'threads': self.threads,
            'timeout': self.timeout
        }

    def reset_statistics(self) -> None:
        """Reset lookup statistics."""
        self._stats = {'forward': 0, 'reverse': 0, 'cached': 0, 'errors': 0}
