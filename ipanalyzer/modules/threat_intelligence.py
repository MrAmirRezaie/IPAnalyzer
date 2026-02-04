"""Simple threat intelligence module using local blacklists."""
from pathlib import Path


class ThreatIntel:
    DEFAULT_BLACKLIST = Path(__file__).resolve().parents[1] / "data" / "blacklist.txt"

    def __init__(self, blacklist_path: str = None):
        self.blacklist = Path(blacklist_path) if blacklist_path else self.DEFAULT_BLACKLIST
        self._load()

    def _load(self):
        self._bl = set()
        try:
            with open(self.blacklist, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self._bl.add(line)
        except Exception:
            self._bl = set()

    def is_blacklisted(self, ip: str) -> bool:
        return ip in self._bl

    def info(self, ip: str) -> dict:
        return {'ip': ip, 'blacklisted': self.is_blacklisted(ip)}
"""
Threat Intelligence - IP reputation and threat analysis module
Provides threat scoring, blacklist management, and threat history tracking.
"""
from typing import List, Dict, Optional, Set, Tuple
import os
from datetime import datetime, timedelta, timezone


class ThreatIntelligence:
    """
    Comprehensive threat intelligence engine for IP reputation analysis.
    
    Performs threat scoring based on multiple data sources including:
    - Local blacklist/whitelist management
    - Threat level classification
    - Risk score calculation
    - Historical threat tracking
    - Threat type categorization
    
    Supports both offline blacklist files and in-memory threat databases.
    """

    # Threat level constants
    THREAT_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
    
    # Common threat types
    THREAT_TYPES = {
        'malware': 'Known malware source',
        'phishing': 'Phishing site detected',
        'proxy': 'Known proxy/VPN service',
        'botnet': 'Botnet C&C or infected host',
        'scanner': 'Known port scanner',
        'spammer': 'Known spam source',
        'exploit': 'Known exploit server',
        'bad_reputation': 'Generally bad reputation'
    }

    def __init__(self, blacklist_path: Optional[str] = None,
                 whitelist_path: Optional[str] = None):
        """
        Initialize threat intelligence engine.
        
        Args:
            blacklist_path: Path to blacklist file. If None, uses default path.
            whitelist_path: Path to whitelist file. If None, uses default path.
        """
        self.blacklist_path = blacklist_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'blacklist.txt'
        )
        self.whitelist_path = whitelist_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'whitelist.txt'
        )
        self._load_blacklist()
        self._load_whitelist()
        self._history = {}
        self._threat_db = self._initialize_threat_db()

    def _load_blacklist(self) -> None:
        """Load blacklist from file."""
        self.blacklist: Set[str] = set()
        try:
            with open(self.blacklist_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.blacklist.add(line)
        except FileNotFoundError:
            self.blacklist = set()

    def _load_whitelist(self) -> None:
        """Load whitelist from file."""
        self.whitelist: Set[str] = set()
        try:
            with open(self.whitelist_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.whitelist.add(line)
        except FileNotFoundError:
            self.whitelist = set()

    def _initialize_threat_db(self) -> Dict[str, Dict]:
        """Initialize in-memory threat database."""
        return {
            # Malware and botnet IPs
            '192.0.2.1': {'threat_type': 'botnet', 'severity': 95, 'details': 'Known botnet C&C'},
            '192.0.2.2': {'threat_type': 'malware', 'severity': 90, 'details': 'Malware distribution'},
            
            # Phishing and phishing hosting
            '198.51.100.1': {'threat_type': 'phishing', 'severity': 85, 'details': 'Phishing hosting'},
            
            # Scanners and reconnaissance
            '203.0.113.1': {'threat_type': 'scanner', 'severity': 60, 'details': 'Port scanner detected'},
        }

    def analyze_threat(self, ip_address: str) -> Dict:
        """
        Comprehensive threat analysis for an IP address.
        
        Args:
            ip_address: IP address to analyze
            
        Returns:
            Dictionary containing:
                - ip: The queried IP address
                - threat_level: Threat classification
                - risk_score: Numeric risk score (0-100)
                - threat_types: List of detected threat types
                - malware: Malware associations
                - exploits: Known exploits
                - last_seen: Last threat activity date
                - sources: Sources reporting threat
                - details: Detailed threat information
        """
        # Check if whitelisted
        if ip_address in self.whitelist:
            record = {
                'ip': ip_address,
                'threat_level': 'UNKNOWN',
                'risk_score': 0,
                'threat_types': [],
                'malware': [],
                'exploits': [],
                'last_seen': datetime.now(timezone.utc).isoformat(),
                'sources': ['whitelist'],
                'details': 'IP is on whitelist',
                'whitelisted': True
            }
            self._history.setdefault(ip_address, []).append(record)
            return record

        # Check if blacklisted
        is_blacklisted = ip_address in self.blacklist
        
        # Check threat database
        threat_info = self._threat_db.get(ip_address, {})
        
        # Calculate threat level and score
        threat_types = []
        base_score = 0
        threat_level = 'LOW'
        
        if is_blacklisted:
            threat_types.append('blacklist')
            base_score += 50
        
        if threat_info:
            threat_type = threat_info.get('threat_type')
            if threat_type:
                threat_types.append(threat_type)
            severity = threat_info.get('severity', 50)
            base_score = max(base_score, severity)
        
        # Determine threat level based on score
        if base_score >= 90:
            threat_level = 'CRITICAL'
        elif base_score >= 70:
            threat_level = 'HIGH'
        elif base_score >= 50:
            threat_level = 'MEDIUM'
        elif base_score >= 20:
            threat_level = 'LOW'
        else:
            threat_level = 'UNKNOWN'
            base_score = 5

        sources = []
        if is_blacklisted:
            sources.append('local-blacklist')
        if threat_info:
            sources.append('threat-database')
        if not sources:
            sources.append('baseline')

        record = {
            'ip': ip_address,
            'threat_level': threat_level,
            'risk_score': base_score,
            'threat_types': threat_types,
            'malware': threat_info.get('malware', []) if threat_info else [],
            'exploits': threat_info.get('exploits', []) if threat_info else [],
            'last_seen': datetime.now(timezone.utc).isoformat(),
            'sources': sources,
            'details': threat_info.get('details', 'No additional details') if threat_info else 'No known threats',
            'whitelisted': False
        }
        
        self._history.setdefault(ip_address, []).append(record)
        return record

    def is_blacklisted(self, ip_address: str) -> bool:
        """
        Check if IP is on blacklist.
        
        Args:
            ip_address: IP to check
            
        Returns:
            True if IP is blacklisted
        """
        return ip_address in self.blacklist

    def is_whitelisted(self, ip_address: str) -> bool:
        """
        Check if IP is on whitelist.
        
        Args:
            ip_address: IP to check
            
        Returns:
            True if IP is whitelisted
        """
        return ip_address in self.whitelist

    def get_threat_history(self, ip_address: str, days: int = 30) -> List[Dict]:
        """
        Get historical threat records for an IP.
        
        Args:
            ip_address: IP to query
            days: Number of days to look back (default: 30)
            
        Returns:
            List of threat records within timeframe
        """
        history = self._history.get(ip_address, [])
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        
        return [record for record in history
                if datetime.fromisoformat(record['last_seen']) > cutoff_time]

    def compare_ips(self, ips: List[str]) -> Dict[str, Dict]:
        """
        Compare threat levels across multiple IPs.
        
        Args:
            ips: List of IP addresses to compare
            
        Returns:
            Dictionary mapping IP to threat analysis
        """
        return {ip: self.analyze_threat(ip) for ip in ips}

    def add_to_blacklist(self, ip_address: str) -> None:
        """
        Add IP to blacklist.
        
        Args:
            ip_address: IP to blacklist
        """
        self.blacklist.add(ip_address)

    def remove_from_blacklist(self, ip_address: str) -> None:
        """
        Remove IP from blacklist.
        
        Args:
            ip_address: IP to remove
        """
        self.blacklist.discard(ip_address)

    def add_to_whitelist(self, ip_address: str) -> None:
        """
        Add IP to whitelist.
        
        Args:
            ip_address: IP to whitelist
        """
        self.whitelist.add(ip_address)

    def remove_from_whitelist(self, ip_address: str) -> None:
        """
        Remove IP from whitelist.
        
        Args:
            ip_address: IP to remove
        """
        self.whitelist.discard(ip_address)

    def export_threat_report(self, ip_address: str, format: str = 'csv') -> str:
        """
        Generate threat report for an IP address.
        
        Args:
            ip_address: IP to report on
            format: Export format ('csv' or 'text')
            
        Returns:
            Formatted report string
        """
        history = self.get_threat_history(ip_address, days=90)
        
        if format == 'csv':
            lines = ['IP,ThreatLevel,RiskScore,ThreatTypes,LastSeen']
            for record in history:
                threat_types = ';'.join(record.get('threat_types', []))
                lines.append(
                    f"{record['ip']},{record['threat_level']},"
                    f"{record['risk_score']},\"{threat_types}\","
                    f"{record['last_seen']}"
                )
            return '\n'.join(lines)
        
        elif format == 'text':
            lines = [f"Threat Report for {ip_address}", "=" * 50]
            if not history:
                lines.append("No threat history found.")
            else:
                for i, record in enumerate(history, 1):
                    lines.append(f"\nRecord {i}:")
                    lines.append(f"  Threat Level: {record['threat_level']}")
                    lines.append(f"  Risk Score: {record['risk_score']}/100")
                    lines.append(f"  Threat Types: {', '.join(record.get('threat_types', ['None']))}")
                    lines.append(f"  Details: {record.get('details', 'N/A')}")
                    lines.append(f"  Last Seen: {record['last_seen']}")
                    lines.append(f"  Sources: {', '.join(record.get('sources', []))}")
            return '\n'.join(lines)
        
        else:
            raise ValueError(f'Unsupported export format: {format}')

    def get_high_risk_ips(self, ips: List[str], threshold: int = 70) -> List[Dict]:
        """
        Filter and identify high-risk IPs from a list.
        
        Args:
            ips: List of IPs to analyze
            threshold: Risk score threshold (default: 70)
            
        Returns:
            List of analysis results for high-risk IPs
        """
        results = []
        for ip in ips:
            analysis = self.analyze_threat(ip)
            if analysis['risk_score'] >= threshold:
                results.append(analysis)
        return results

    def get_statistics(self) -> Dict:
        """
        Get threat intelligence statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'blacklist_size': len(self.blacklist),
            'whitelist_size': len(self.whitelist),
            'threat_db_entries': len(self._threat_db),
            'total_analyzed': len(self._history),
            'history_records': sum(len(v) for v in self._history.values())
        }

    def clear_history(self, days_old: int = 90) -> int:
        """
        Clear old threat history.
        
        Args:
            days_old: Clear records older than this many days
            
        Returns:
            Number of records removed
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_old)
        removed = 0
        
        for ip in list(self._history.keys()):
            old_records = [r for r in self._history[ip]
                          if datetime.fromisoformat(r['last_seen']) < cutoff_time]
            removed += len(old_records)
            self._history[ip] = [r for r in self._history[ip]
                                if datetime.fromisoformat(r['last_seen']) >= cutoff_time]
            if not self._history[ip]:
                del self._history[ip]
        
        return removed
