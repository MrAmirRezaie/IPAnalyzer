"""Simple HTML report generator."""
from typing import Any, Dict


class ReportGenerator:
    def generate_html(self, data: Dict[str, Any]) -> str:
        parts = ["<html><head><meta charset='utf-8'><title>IPAnalyzer Report</title></head><body>"]
        parts.append("<h1>IPAnalyzer Report</h1>")
        parts.append("<pre>")
        import json
        parts.append(json.dumps(data, indent=2))
        parts.append("</pre>")
        parts.append("</body></html>")
        return '\n'.join(parts)

    def save(self, html: str, path: str):
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(html)
"""
Report Generator Module
Generate professional HTML reports for IP analysis
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class ReportGenerator:
    """Generate HTML reports for IP analysis"""
    
    def __init__(self):
        """Initialize Report Generator"""
        self.author = "MrAmirRezaie"
        self.tool_name = "IPAnalyzer"
        self.version = "1.0.0"
    
    def generate_html_report(self, data: Dict, output_file: str = None) -> str:
        """
        Generate comprehensive HTML report
        Returns HTML content
        """
        html = self._get_html_header()
        html += self._get_styles()
        html += '<body>'
        
        # Header
        html += self._get_header_section()
        
        # Main content
        if 'ip' in data:
            html += self._get_ip_analysis_section(data)
        
        if 'devices' in data:
            html += self._get_devices_section(data['devices'])
        
        if 'ranges' in data:
            html += self._get_ranges_section(data)
        
        # Footer
        html += self._get_footer_section()
        
        html += '</body></html>'
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    def _get_html_header(self) -> str:
        """Get HTML document header"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPAnalyzer Report</title>
</head>
"""
    
    def _get_styles(self) -> str:
        """Get CSS styles"""
        return """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #333;
        line-height: 1.6;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .header {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
        border-left: 5px solid #667eea;
    }
    
    .header h1 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 2.5em;
    }
    
    .header p {
        color: #666;
        font-size: 0.95em;
    }
    
    .meta-info {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
        font-size: 0.9em;
        color: #555;
    }
    
    .meta-item {
        padding: 10px;
        background: #f5f5f5;
        border-radius: 5px;
        border-left: 3px solid #667eea;
    }
    
    .section {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .section h2 {
        color: #667eea;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #667eea;
        font-size: 1.8em;
    }
    
    .section h3 {
        color: #764ba2;
        margin-top: 20px;
        margin-bottom: 15px;
        font-size: 1.3em;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    .info-box label {
        display: block;
        color: #666;
        font-size: 0.85em;
        margin-bottom: 5px;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .info-box .value {
        font-size: 1.1em;
        color: #333;
        font-family: 'Courier New', monospace;
        word-break: break-all;
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .status-active {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-inactive {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .status-private {
        background-color: #cce5ff;
        color: #004085;
    }
    
    .status-public {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .table-wrapper {
        overflow-x: auto;
        margin-bottom: 20px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95em;
    }
    
    table thead {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    table th {
        padding: 15px;
        text-align: left;
        font-weight: 600;
    }
    
    table td {
        padding: 12px 15px;
        border-bottom: 1px solid #eee;
    }
    
    table tbody tr:hover {
        background-color: #f9f9f9;
    }
    
    table tbody tr:nth-child(even) {
        background-color: #fafafa;
    }
    
    .footer {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: #666;
        font-size: 0.9em;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    
    .footer p {
        margin: 5px 0;
    }
    
    .highlight {
        background-color: #fff9e6;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 500;
    }
    
    .warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .success {
        background-color: #d4edda;
        border: 1px solid #28a745;
        color: #155724;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 0.85em;
        font-weight: 600;
        background-color: #e9ecef;
        color: #495057;
    }
    
    .chart {
        margin: 20px 0;
    }
    
    @media (max-width: 768px) {
        .header h1 {
            font-size: 1.8em;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
        }
        
        table {
            font-size: 0.85em;
        }
        
        table th, table td {
            padding: 10px;
        }
    }
</style>
"""
    
    def _get_header_section(self) -> str:
        """Get header section HTML"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
<div class="container">
    <div class="header">
        <h1>🔍 {self.tool_name}</h1>
        <p>Advanced IP Analysis Report</p>
        <div class="meta-info">
            <div class="meta-item"><strong>Generated:</strong> {timestamp}</div>
            <div class="meta-item"><strong>Tool:</strong> {self.tool_name} v{self.version}</div>
            <div class="meta-item"><strong>Author:</strong> {self.author}</div>
        </div>
    </div>
"""
    
    def _get_ip_analysis_section(self, data: Dict) -> str:
        """Generate IP analysis section"""
        ip = data.get('ip', 'N/A')
        classification = data.get('classification', 'Unknown')
        is_private = data.get('is_private', False)
        whois_info = data.get('whois', {})
        
        section = f"""
    <div class="section">
        <h2>📍 IP Analysis</h2>
        
        <div class="info-grid">
            <div class="info-box">
                <label>IP Address</label>
                <div class="value">{ip}</div>
            </div>
            
            <div class="info-box">
                <label>Classification</label>
                <div class="value">
                    <span class="status-badge status-{'private' if is_private else 'public'}">{classification}</span>
                </div>
            </div>
"""
        
        if whois_info.get('source') == 'local_database' or whois_info.get('organization'):
            section += f"""
            <div class="info-box">
                <label>Organization</label>
                <div class="value">{whois_info.get('organization', 'N/A')}</div>
            </div>
            
            <div class="info-box">
                <label>Country</label>
                <div class="value">{whois_info.get('country', 'N/A')}</div>
            </div>
            
            <div class="info-box">
                <label>IP Range</label>
                <div class="value">{whois_info.get('range', 'N/A')}</div>
            </div>
            
            <div class="info-box">
                <label>RIR</label>
                <div class="value">{whois_info.get('rir', 'N/A')}</div>
            </div>
"""
        
        if whois_info.get('source') == 'unavailable':
            section += """
            <div class="warning">
                ⚠️ WHOIS information unavailable. This IP may be private or not yet registered.
            </div>
"""
        
        section += """
        </div>
    </div>
"""
        return section
    
    def _get_devices_section(self, devices: List[Dict]) -> str:
        """Generate devices section"""
        section = """
    <div class="section">
        <h2>🖥️ Connected Devices</h2>
"""
        
        if not devices:
            section += """
        <div class="warning">
            No devices found on the network.
        </div>
"""
        else:
            section += f"""
        <p style="margin-bottom: 15px;"><strong>Total Devices Found:</strong> {len(devices)}</p>
        
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>MAC Address</th>
                        <th>Hostname</th>
                        <th>Vendor</th>
                        <th>Status</th>
                        <th>Method</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for device in devices:
                ip = device.get('ip', 'N/A')
                mac = device.get('mac', 'N/A')
                hostname = device.get('hostname', 'N/A')
                vendor = device.get('vendor', 'N/A')
                status = device.get('status', 'unknown')
                method = device.get('method', 'N/A')
                
                status_class = 'status-active' if status == 'active' else 'status-inactive'
                
                section += f"""
                    <tr>
                        <td><span class="highlight">{ip}</span></td>
                        <td><code>{mac}</code></td>
                        <td>{hostname}</td>
                        <td><span class="badge">{vendor}</span></td>
                        <td><span class="status-badge {status_class}">{status.upper()}</span></td>
                        <td>{method.upper()}</td>
                    </tr>
"""
            
            section += """
                </tbody>
            </table>
        </div>
"""
        
        section += """
    </div>
"""
        return section
    
    def _get_ranges_section(self, data: Dict) -> str:
        """Generate IP ranges section"""
        ranges = data.get('ranges', [])
        
        section = """
    <div class="section">
        <h2>📊 IP Range Analysis</h2>
"""
        
        if isinstance(ranges, list) and len(ranges) > 0:
            for range_info in ranges:
                cidr = range_info.get('cidr', 'N/A')
                network_ip = range_info.get('network_ip', 'N/A')
                broadcast_ip = range_info.get('broadcast_ip', 'N/A')
                netmask = range_info.get('netmask', 'N/A')
                prefix = range_info.get('prefix_length', 'N/A')
                total_hosts = range_info.get('total_addresses', 0)
                usable_hosts = range_info.get('usable_hosts', 0)
                ip_class = range_info.get('ip_class', 'N/A')
                first_usable = range_info.get('first_usable', 'N/A')
                last_usable = range_info.get('last_usable', 'N/A')
                
                section += f"""
        <h3>Range: {cidr}</h3>
        <div class="info-grid">
            <div class="info-box">
                <label>CIDR</label>
                <div class="value">{cidr}</div>
            </div>
            
            <div class="info-box">
                <label>Network IP</label>
                <div class="value">{network_ip}</div>
            </div>
            
            <div class="info-box">
                <label>Broadcast IP</label>
                <div class="value">{broadcast_ip}</div>
            </div>
            
            <div class="info-box">
                <label>Subnet Mask</label>
                <div class="value">{netmask}</div>
            </div>
            
            <div class="info-box">
                <label>Prefix Length</label>
                <div class="value">/{prefix}</div>
            </div>
            
            <div class="info-box">
                <label>IP Class</label>
                <div class="value">{ip_class}</div>
            </div>
            
            <div class="info-box">
                <label>Total Addresses</label>
                <div class="value">{total_hosts}</div>
            </div>
            
            <div class="info-box">
                <label>Usable Hosts</label>
                <div class="value">{usable_hosts}</div>
            </div>
            
            <div class="info-box">
                <label>First Usable IP</label>
                <div class="value">{first_usable}</div>
            </div>
            
            <div class="info-box">
                <label>Last Usable IP</label>
                <div class="value">{last_usable}</div>
            </div>
        </div>
"""
        else:
            section += """
        <div class="warning">
            No IP range data available.
        </div>
"""
        
        section += """
    </div>
"""
        return section
    
    def _get_footer_section(self) -> str:
        """Get footer section HTML"""
        return f"""
    <div class="footer">
        <p><strong>{self.tool_name}</strong> v{self.version}</p>
        <p>Created by <strong>{self.author}</strong></p>
        <p>© 2026 - Advanced IP Analysis Tool</p>
    </div>
</div>
"""
