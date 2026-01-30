"""Bulk DNS processing utilities"""
from typing import List, Dict
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


class DNSBulkProcessor:
    """Perform batch forward and reverse DNS lookups using threads."""

    def __init__(self, threads: int = 8, timeout: int = 5):
        self.threads = max(1, int(threads))
        self.timeout = timeout
        # Ensure socket timeout for lookups
        socket.setdefaulttimeout(self.timeout)

    def _forward(self, hostname: str) -> Dict:
        try:
            infos = socket.getaddrinfo(hostname, None)
            ips = sorted({item[4][0] for item in infos})
            return {'hostname': hostname, 'ips': ips, 'error': None}
        except Exception as e:
            return {'hostname': hostname, 'ips': [], 'error': str(e)}

    def _reverse(self, ip: str) -> Dict:
        try:
            name = socket.gethostbyaddr(ip)[0]
            return {'ip': ip, 'hostname': name, 'error': None}
        except Exception as e:
            return {'ip': ip, 'hostname': None, 'error': str(e)}

    def forward_lookup_batch(self, hostnames: List[str]) -> Dict[str, Dict]:
        results = {}
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self._forward, h): h for h in hostnames}
            for fut in as_completed(futures):
                res = fut.result()
                results[res['hostname']] = res
        return results

    def reverse_lookup_batch(self, ips: List[str]) -> Dict[str, Dict]:
        results = {}
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self._reverse, ip): ip for ip in ips}
            for fut in as_completed(futures):
                res = fut.result()
                results[res.get('ip')] = res
        return results

    def batch_from_file(self, filepath: str, reverse: bool = False) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
        return self.reverse_lookup_batch(lines) if reverse else self.forward_lookup_batch(lines)

    def export_results(self, results: Dict, format: str = 'csv') -> str:
        if format == 'csv':
            lines = []
            for key, val in results.items():
                if 'hostname' in val:
                    lines.append(f"{val.get('ip','')},{val.get('hostname','')},\"{val.get('error') or ''}\"")
                else:
                    lines.append(f"{val.get('hostname','')},{';'.join(val.get('ips',[]))},\"{val.get('error') or ''}\"")
            return '\n'.join(lines)
        raise ValueError('Unsupported export format')
