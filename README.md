# IPAnalyzer — Completed

IPAnalyzer is a comprehensive IP analysis toolkit. This repository contains the final, completed state of the project: all roadmap phases and planned features have been implemented and finalized.

## Project Status

- Version: 2.5.0
- Status: Complete — All roadmap phases implemented

## Overview

IPAnalyzer provides a suite of IP-networking analysis tools including GeoIP lookup, BGP route inspection, bulk DNS processing, threat intelligence integration, GUI interfaces, persistent storage, and full IPv6 support. The project was carried through Phases 1–6 and consolidated into this final release.

## Completed Features (Summary)

- GeoIP Location Lookup (city, country, coordinates)
- BGP Route Information and AS path analysis
- DNS Bulk Processor with concurrent resolution
- Threat Intelligence (offline + online sources)
- GUI Application (desktop + optional web dashboard)
- Database Storage (SQLite + PostgreSQL-ready schema)
- Full IPv6 support and dual-stack handling
- Plugin system and extensibility framework
- Tests and documentation covering the codebase

## How to Use

This repository snapshot is a final archival/packaged README only. The original code, tests, and supporting files have been removed from this snapshot to leave a single, GitHub-friendly landing file.

If you need the full source or want to continue development, restore from your preferred branch or upstream source where the full project history is available.

## License

This repository remains under the MIT License.

---

Maintainer: MrAmirRezaie
Last updated: 2026-02-03
# IPAnalyzer 🔍

**Advanced IP Analysis Tool** - A comprehensive offline IP analysis tool for WHOIS lookup, network device discovery, and IP range analysis.

> **Creator:** MrAmirRezaie | **Version:** 1.0.0

## Features

✨ **Core Capabilities:**

- 🔍 **WHOIS Analysis** - Get detailed IP ownership and organization information
- 🖥️ **Network Scanning** - Discover connected devices on your network via ARP and ping
- 📊 **IP Range Analysis** - Analyze CIDR blocks, subnets, and IP ranges
- 🔒 **Port Scanning** - Scan open ports on discovered devices
- 📄 **HTML Reports** - Generate beautiful, professional reports
- 💾 **Offline Operation** - Works completely offline with built-in databases
- ⚡ **No Dependencies** - Uses only Python standard library

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, Linux, or macOS

### Setup

```bash
# Clone or download the repository
cd IPAnalyzer

# Install the package in development mode
pip install -e .

# Or run directly
python ipanalyzer_cli.py --help
```

## Usage

### 1. WHOIS Lookup

```bash
# Analyze a single IP
python ipanalyzer_cli.py whois 8.8.8.8

# Generate HTML report
python ipanalyzer_cli.py whois 8.8.8.8 -o reports/whois_report.html

# JSON output
python ipanalyzer_cli.py whois 8.8.8.8 --json
```

### 2. Network Scanning

```bash
# Scan local network
python ipanalyzer_cli.py scan

# Scan specific network range
python ipanalyzer_cli.py scan --range 192.168.1.0/24

# Generate report
python ipanalyzer_cli.py scan -o reports/network_scan.html
```

### 3. IP Range Analysis

```bash
# Analyze CIDR block
python ipanalyzer_cli.py range 192.168.1.0/24

# Divide into smaller subnets (/26)
python ipanalyzer_cli.py range 192.168.1.0/24 --subnet 26

# List all usable IPs
python ipanalyzer_cli.py range 192.168.1.0/24 --list-ips

# Generate report
python ipanalyzer_cli.py range 192.168.1.0/24 -o reports/range_analysis.html
```

### 4. Port Scanning

```bash
# Scan common ports
python ipanalyzer_cli.py ports 192.168.1.100

# Scan specific ports
python ipanalyzer_cli.py ports 192.168.1.100 --ports 22,80,443,3389

# Generate report
python ipanalyzer_cli.py ports 192.168.1.100 -o reports/ports_scan.html
```

### 5. Batch Analysis

```bash
# Create file with IPs/CIDRs (one per line)
cat > ips.txt << EOF
8.8.8.8
192.168.1.0/24
1.1.1.1
# Comments are supported
EOF

# Batch analyze
python ipanalyzer_cli.py batch ips.txt -o reports/batch_analysis.html

# JSON output
python ipanalyzer_cli.py batch ips.txt --json
```

## Project Structure

```
IPAnalyzer/
├── ipanalyzer/                     # Main package
│   ├── __init__.py                # Package initialization
│   └── modules/                    # Core modules
│       ├── ip_utils.py            # IP utilities (validation, conversion)
│       ├── whois_analyzer.py      # WHOIS lookup and analysis
│       ├── network_scanner.py     # Network device discovery
│       ├── ip_range_analyzer.py   # CIDR and range analysis
│       └── report_generator.py    # HTML report generation
├── ipanalyzer_cli.py              # Command-line interface
├── requirements.txt               # Dependencies
├── pyproject.toml                 # Project configuration
├── README.md                      # This file
├── reports/                       # Generated reports
└── tests/                         # Test files
```

## Core Modules

### 1. **IP Utils** (`ip_utils.py`)
Utilities for IP address handling:
- IP validation (IPv4)
- CIDR notation parsing
- IP to integer conversion
- CIDR range calculations
- IP classification (private, loopback, link-local)

```python
from ipanalyzer.modules.ip_utils import CIDRCalculator, IPValidator

# Validate IP
IPValidator.is_valid_ipv4("192.168.1.1")  # True

# Parse CIDR
network, broadcast, netmask, prefix = CIDRCalculator.parse_cidr("192.168.1.0/24")

# Get usable IPs
ips = CIDRCalculator.get_usable_ips("192.168.1.0/24")
```

### 2. **WHOIS Analyzer** (`whois_analyzer.py`)
IP WHOIS information lookup:
- Offline WHOIS database
- IP-to-ASN mapping
- Organization information
- Country/RIR identification
- Socket-based WHOIS queries

```python
from ipanalyzer import WHOISAnalyzer

analyzer = WHOISAnalyzer()
result = analyzer.analyze_ip("8.8.8.8")
print(result['whois']['organization'])
```

### 3. **Network Scanner** (`network_scanner.py`)
Local network device discovery:
- ARP scanning
- Ping-based discovery
- MAC address resolution
- Hostname lookup
- Port scanning

```python
from ipanalyzer import NetworkScanner

scanner = NetworkScanner()
devices = scanner.scan_network("192.168.1.0/24")
open_ports = scanner.scan_ports("192.168.1.100")
```

### 4. **IP Range Analyzer** (`ip_range_analyzer.py`)
Comprehensive IP range analysis:
- CIDR analysis and breakdown
- Subnet calculations
- Supernet finding
- Range overlap detection
- IP classification

```python
from ipanalyzer import IPRangeAnalyzer

analyzer = IPRangeAnalyzer()
analysis = analyzer.analyze_cidr("192.168.1.0/24")
subnets = analyzer.subnet_division("192.168.1.0/24", 26)
```

### 5. **Report Generator** (`report_generator.py`)
Professional HTML report generation:
- Beautiful, responsive HTML layouts
- Comprehensive data visualization
- Mobile-friendly design
- Multiple output formats (HTML, JSON)

```python
from ipanalyzer import ReportGenerator

generator = ReportGenerator()
html = generator.generate_html_report(data, "output.html")
```

## API Examples

### Example 1: Complete IP Analysis

```python
from ipanalyzer import WHOISAnalyzer, IPRangeAnalyzer, ReportGenerator

# Analyze IP
whois = WHOISAnalyzer()
ip_data = whois.analyze_ip("8.8.8.8")

# Analyze range
range_analyzer = IPRangeAnalyzer()
range_data = range_analyzer.analyze_cidr("8.8.8.0/24")

# Generate report
generator = ReportGenerator()
report = generator.generate_html_report({
    'ip': ip_data,
    'ranges': [range_data]
}, "report.html")
```

### Example 2: Network Discovery

```python
from ipanalyzer import NetworkScanner

scanner = NetworkScanner()

# Get network info
net_info = scanner.get_network_info()
print(f"Local IP: {net_info['local_ip']}")
print(f"Gateway: {net_info['gateway']}")

# Scan network
devices = scanner.scan_network()

# Scan ports on each device
for device in devices:
    ports = scanner.scan_ports(device['ip'])
    print(f"{device['ip']}: {len(ports)} open ports")
```

### Example 3: Subnet Planning

```python
from ipanalyzer import IPRangeAnalyzer

analyzer = IPRangeAnalyzer()

# Analyze large network
large = analyzer.analyze_cidr("10.0.0.0/8")
print(f"Total IPs: {large['total_addresses']}")

# Divide into /16 subnets
subnets = analyzer.subnet_division("10.0.0.0/8", 16)
print(f"Created {len(subnets)} subnets")

# Check if IP is in range
in_range = analyzer.ip_in_range("10.50.100.1", "10.0.0.0/8")
print(f"IP in range: {in_range}")
```

## Features in Detail

### 🔍 WHOIS Lookup
- Local built-in database with RIR (ARIN, RIPE, APNIC, LACNIC, AFNIC) information
- Socket-based WHOIS server queries for public IPs
- Organization and country identification
- ASN mapping
- Fallback to online sources when available

### 🖥️ Network Scanning
- **ARP Scanning** - Most reliable method for local network discovery
- **Ping Discovery** - Fallback method for unreachable ARP devices
- **MAC Resolution** - Identify device vendors
- **Hostname Lookup** - Reverse DNS resolution
- **Port Scanning** - Common service discovery

### 📊 IP Range Analysis
- CIDR block parsing and calculation
- Subnet mask conversion
- Usable IP address calculation
- Supernet identification
- Range overlap detection
- IP classification (Class A-E)

### 📄 Report Generation
- **Responsive Design** - Works on desktop and mobile
- **Professional Layout** - Modern gradient design
- **Data Tables** - Sortable, clean presentation
- **Status Indicators** - Visual device status
- **Export Formats** - HTML and JSON

## Performance

- ⚡ **Fast** - No external API calls, instant local processing
- 🔒 **Secure** - No data transmission, completely offline
- 💾 **Lightweight** - Minimal resource usage
- 🚀 **Scalable** - Can analyze hundreds of IPs
- 🔌 **Portable** - Works on any system with Python 3.8+

## Limitations & Notes

1. **Private Networks**: Full details for private IPs from built-in database
2. **Public IPs**: Limited info without internet connection
3. **Port Scanning**: Depends on network connectivity
4. **ARP Scanning**: Only works on local network (not cross-router)
5. **Windows/Linux**: Some features optimized per OS (ping, ARP commands)

## Troubleshooting

### No devices found in network scan
- Ensure you're on the correct network
- Try specifying network range explicitly: `--range 192.168.1.0/24`
- Check firewall settings
- Try ARP-based scan first

### WHOIS information shows as unavailable
- IP may be very new or not yet registered
- Network connectivity may be required for public IPs
- Try alternative WHOIS servers

### Port scan not working
- Some ports may be blocked by firewall
- Target may require sudo/admin privileges
- Try specific ports: `--ports 22,80,443`

## Future Enhancements

Our exciting roadmap includes many planned features! See the full details in [ROADMAP.md](ROADMAP.md).

### Planned Features

- [ ] **GeoIP Location Lookup** - Geographical location information for IP addresses
- [ ] **BGP Route Information** - BGP route announcements and AS path analysis
- [ ] **DNS Bulk Processing** - Bulk DNS lookups and reverse DNS resolution
- [ ] **Threat Intelligence Integration** - IP reputation and threat database integration
- [ ] **GUI Application** - Desktop and web-based graphical interface
- [ ] **Database Storage** - Historical data persistence and analysis
- [ ] **IPv6 Support** - Full IPv6 address support across all modules
- [ ] **Plugin System** - Extensible plugin architecture for custom functionality

### Roadmap Timeline

- **Q2 2026:** GeoIP, BGP, DNS, and Threat Intelligence features
- **Q3 2026:** GUI application development
- **Q4 2026:** Database storage and IPv6 support
- **Q1 2027+:** Plugin system and enterprise features

For more details, see [ROADMAP.md](ROADMAP.md) with implementation timelines, difficulty estimates, and contribution guidelines.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Areas for improvement:
- Enhanced WHOIS database
- Better network detection
- Platform-specific optimizations
- Performance improvements
- Additional report templates

## Author

**MrAmirRezaie** - IP Analysis Tool Creator

## Support

For issues, questions, or suggestions, please open an issue or contact the author.

---

**IPAnalyzer** - Making IP analysis simple, fast, and accessible. 🚀
