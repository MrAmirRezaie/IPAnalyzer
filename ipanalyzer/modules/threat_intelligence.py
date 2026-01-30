"""Threat intelligence minimal integration using local lists."""
from typing import List, Dict
import os
from datetime import datetime


class ThreatIntelligence:
    """Simple local threat intelligence manager.

    Uses a local blacklist file (one IP or CIDR per line) if present.
    Provides simple scoring and history storage (in-memory).
    """

    def __init__(self, blacklist_path: str = None):
        self.blacklist_path = blacklist_path or os.path.join(os.path.dirname(__file__), '..', 'data', 'blacklist.txt')
        self._load_blacklist()
        self._history = {}

    def _load_blacklist(self):
        self.blacklist = set()
        try:
            with open(self.blacklist_path, 'r', encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith('#'):
                        continue
                    self.blacklist.add(ln)
        except FileNotFoundError:
            self.blacklist = set()

    def analyze_threat(self, ip_address: str) -> Dict:
        # Simple heuristics: blacklist membership -> HIGH
        is_blacklisted = ip_address in self.blacklist
        score = 80 if is_blacklisted else 5
        level = 'HIGH' if is_blacklisted else 'LOW'
        rec = {
            'ip': ip_address,
            'threat_level': level,
            'risk_score': score,
            'threat_types': ['blacklist'] if is_blacklisted else [],
            'last_seen': datetime.utcnow().isoformat(),
            'sources': ['local-blacklist' if is_blacklisted else 'none']
        }
        self._history.setdefault(ip_address, []).append(rec)
        return rec

    def is_blacklisted(self, ip_address: str) -> bool:
        return ip_address in self.blacklist

    def get_threat_history(self, ip_address: str) -> List[Dict]:
        return self._history.get(ip_address, [])

    def compare_ips(self, ips: List[str]) -> Dict[str, Dict]:
        return {ip: self.analyze_threat(ip) for ip in ips}

    def export_threat_report(self, ip_address: str) -> str:
        history = self.get_threat_history(ip_address)
        lines = [f"IP,ThreatLevel,RiskScore,LastSeen"]
        for h in history:
            lines.append(f"{h['ip']},{h['threat_level']},{h['risk_score']},{h['last_seen']}")
        return '\n'.join(lines)
