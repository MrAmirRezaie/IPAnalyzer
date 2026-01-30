"""Database manager using SQLite for local persistent storage."""
import sqlite3
from typing import Optional, List, Dict
import os
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self, db_type: str = 'sqlite', db_path: Optional[str] = None):
        if db_type != 'sqlite':
            raise NotImplementedError('Only sqlite backend is implemented')
        self.db_path = db_path or os.path.join(os.getcwd(), 'ip_analyzer_data.sqlite')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._initialize_schema()

    def _initialize_schema(self):
        cur = self.conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            analysis_type TEXT,
            data TEXT,
            created_at TEXT
        )
        ''')
        cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_analyses_ip ON analyses(ip)
        ''')
        self.conn.commit()

    def store_analysis(self, analysis_type: str, data: Dict) -> int:
        cur = self.conn.cursor()
        ip = data.get('ip') or data.get('network') or ''
        cur.execute('INSERT INTO analyses (ip, analysis_type, data, created_at) VALUES (?, ?, ?, ?)',
                    (ip, analysis_type, str(data), datetime.utcnow().isoformat()))
        self.conn.commit()
        return cur.lastrowid

    def query_history(self, ip_address: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute('SELECT id, ip, analysis_type, data, created_at FROM analyses WHERE ip = ? ORDER BY created_at DESC', (ip_address,))
        rows = cur.fetchall()
        return [{'id': r[0], 'ip': r[1], 'type': r[2], 'data': r[3], 'created_at': r[4]} for r in rows]

    def export_data(self, format: str = 'csv') -> str:
        cur = self.conn.cursor()
        cur.execute('SELECT id, ip, analysis_type, data, created_at FROM analyses')
        rows = cur.fetchall()
        if format == 'csv':
            lines = ['id,ip,analysis_type,created_at,data']
            for r in rows:
                lines.append(f'"{r[0]}","{r[1]}","{r[2]}","{r[4]}","{r[3]}"')
            return '\n'.join(lines)
        raise ValueError('Unsupported export format')

    def cleanup_old_records(self, days: int = 90):
        cutoff = datetime.utcnow() - timedelta(days=days)
        cur = self.conn.cursor()
        cur.execute('DELETE FROM analyses WHERE created_at < ?', (cutoff.isoformat(),))
        self.conn.commit()
