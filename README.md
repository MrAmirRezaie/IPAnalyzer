# IPAnalyzer — A Complete Guide

IPAnalyzer is a modular, extensible toolkit for offline IP and network analysis. It is focused on delivering reliable, auditable, and testable components for GeoIP lookup, BGP/ASN mapping, threat intelligence, DNS processing, WHOIS parsing, IP-range analysis, and report generation.

This README documents: installation, CLI usage, Python API examples, module internals, data sources and accuracy considerations, project structure, testing, CI guidance, and contribution guidelines. It is intended to be a single source-of-truth for contributors and users.

---

Table of Contents
- Overview
- Quick Features
- Project Accuracy & Data Sources
- Installation
- Configuration
- CLI Quick Start
- Python API Reference (examples)
- Project Structure (detailed)
- Module Internals and Behavior
- Data, Caching & Persistence
- Testing & CI
- Troubleshooting
- Contribution Guide
- License & Contact

---

Overview
--------
IPAnalyzer is intentionally small and modular. Each module under `ipanalyzer/modules/` implements a clear responsibility and a simple, well-documented API. The library aims to be usable entirely offline with local data shipped in `ipanalyzer/data/`, while optionally allowing online lookups for extended functionality.

Quick Features
--------------
- GeoIP lookup: city, country, latitude/longitude (local CSV fallback)
- BGP prefix table: map IPs -> ASN, AS name, and simple offline AS-path tracing
- Threat intelligence: blacklist/whitelist handling and a compact in-memory threat DB
- WHOIS helpers: lightweight parsing and offline fallbacks with socket WHOIS as an option
- IP utilities: CIDR parsing, IP <-> integer conversions, subnet operations
- Report generation: HTML and JSON reporting utilities
- CLI wrapper: easy access to common commands for quick analysis and batch jobs

Project Accuracy & Data Sources
------------------------------
Accuracy depends on the data used by modules. By default the project uses small sample datasets included in `ipanalyzer/data/` for offline operation. These are suitable for unit tests, examples, and lightweight demonstrations but are NOT comprehensive production datasets.

Data sources and guidance:
- GeoIP: local CSV (sample) — accuracy depends on the CSV source you provide. For production accuracy, replace `geoip_db.csv` with a reputable provider (MaxMind, IP2Location, etc.) and follow their licensing.
- BGP/ASN: small offline prefix table (`_SAMPLE_PREFIXES`) — intended for examples and tests. For real routing accuracy, use a current BGP dump or routeviews snapshots and update the prefix table regularly.
- Threat intelligence: local plain-text blacklists are only as accurate as the lists you provide. Combine multiple curated sources and maintain retention policies for `last_seen` timestamps.

If you need to use IPAnalyzer in production, replace the included sample DBs with regularly-updated datasets and document their provenance and update cadence in your deployment.

Installation
------------
Prerequisites:
- Python 3.8 or later

Recommended quick setup (Windows example shown):

```powershell
git clone https://github.com/MrAmirRezaie/IPAnalyzer.git
cd IPAnalyzer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # if present
```

On macOS / Linux:

```bash
git clone https://github.com/MrAmirRezaie/IPAnalyzer.git
cd IPAnalyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # if present
```

Configuration
-------------
Most modules accept optional parameters to override default data paths. Common environment / config options:

- `IPANALYZER_GEOIP_DB` — path to a GeoIP CSV to load instead of the sample
- `IPANALYZER_BLACKLIST` — path to a plaintext blacklist file (one IP per line)

You may also pass file paths directly when creating module instances in code (e.g., `GeoIPAnalyzer(db=my_db)`).

CLI Quick Start
---------------
The repository includes `ipanalyzer_cli.py` which exposes common commands. Basic usage:

```bash
python ipanalyzer_cli.py --help
```

Examples:

- GeoIP lookup for a single IP:
```bash
python ipanalyzer_cli.py geoip 8.8.8.8
```

- WHOIS lookup (local helper):
```bash
python ipanalyzer_cli.py whois 8.8.8.8
```

- Batch analyze a file of IPs/CIDRs:
```bash
python ipanalyzer_cli.py batch ips.txt -o reports/batch_analysis.html
```

Python API Reference — Examples
--------------------------------
GeoIP (basic):

```python
from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer

geo = GeoIPAnalyzer()
print(geo.analyze('8.8.8.8'))
print(geo.batch_analyze(['8.8.8.8', '1.1.1.1']))
```

BGP/ASN mapping:

```python
from ipanalyzer.modules.bgp_analyzer import BGPAnalyzer

b = BGPAnalyzer()
print(b.analyze_ip('8.8.8.8'))
print(b.get_as_info(15169))
```

Threat Intelligence:

```python
from ipanalyzer.modules.threat_intelligence import ThreatIntelligence

ti = ThreatIntelligence()
print(ti.analyze_threat('192.0.2.1'))
print(ti.get_threat_history('192.0.2.1'))
```

Project Structure (detailed)
----------------------------
Top-level layout (descriptions):

```
IPAnalyzer/
├── ipanalyzer/                     # Main Python package
│   ├── __init__.py                 # Package initialization and exports
│   ├── data/                       # Small sample data shipped with package
│   │   ├── blacklist.txt
│   │   └── geoip_db.csv
│   ├── gui/                        # Optional desktop GUI launcher
│   ├── modules/                    # Functional modules (core of the project)
│   │   ├── bgp_analyzer.py         # Offline BGP prefix->ASN mapping
│   │   ├── geoip_analyzer.py       # GeoIP lookup with CSV fallback
│   │   ├── whois_analyzer.py       # WHOIS helpers and parsers
│   │   ├── ip_range_analyzer.py    # CIDR and range utilities
│   │   ├── ip_utils.py             # Utility helpers for IP operations
│   │   ├── network_scanner.py      # Local network scanning helpers
│   │   ├── threat_intelligence.py  # Local threat scoring and history
│   │   └── report_generator.py     # HTML/JSON reporting helpers
│   └── storage/                    # Optional persistence helpers (SQLite manager)
├── ipanalyzer_cli.py               # Command-line entrypoint and argument parsing
├── tests/                          # Unit tests and test fixtures
├── requirements.txt                # Optional dependency list
├── pyproject.toml                  # Packaging configuration
├── ROADMAP.md                       # Feature roadmap and timeline
└── README.md                       # This file
```

Module Internals and Behavior
-----------------------------
The following describes internal choices and trade-offs made in the implementation.

GeoIP:
- Uses linear search over a list of (start_int, end_int, meta) tuples. This is easy to implement and sufficient for small databases. For larger DBs, replace with a radix tree (py-radix) or store in a SQLite table with indexed start/end ranges.
- `GeoIPAnalyzer.batch_analyze` and `batch_lookup` provide bulk processing convenience; results are cached in-memory to speed repeated lookups.

BGP Analyzer:
- Offline sample prefixes are stored as integer ranges. Matching is performed via linear search; for production use, convert to a prefix trie or radix structure.
- `analyze_ip()` returns `{'ip': ip, 'asn': 'AS15169', 'name': 'GOOGLE', 'country': 'US'}` for matched prefixes.

Threat Intelligence:
- Maintains an in-memory `_threat_db` and persistent local blacklist file. Records in history include timezone-aware `last_seen` timestamps and basic metadata.
- `analyze_threat()` produces reproducible records for unit tests and simple scoring.

Data, Caching & Persistence
--------------------------
- Small sample data files are in `ipanalyzer/data/`. Replace these with production datasets as needed.
- Modules may implement simple in-memory caching (`_cache`) to avoid repeated heavy computations during a single run.
- For persistent history or larger datasets, the `ipanalyzer/storage/database_manager.py` provides an example SQLite manager (optional and lightweight).

Testing & Continuous Integration
--------------------------------
Unit tests are provided; run them with pytest:

```bash
.venv\Scripts\python -m pytest -q
```

Recommended CI pipeline (GitHub Actions):
- Use Python 3.8/3.10 runners
- Install dependencies into a venv
- Run `pytest -q` and `flake8`/`pylint` if desired
- Optionally run mypy/static type checks

Troubleshooting
---------------
- `pytest` not found: install into the venv with `pip install pytest` or run via venv Python as shown above.
- GeoIP returns minimal data: replace `ipanalyzer/data/geoip_db.csv` with a fuller dataset.
- BGP results are basic: update the `_SAMPLE_PREFIXES` or point the BGP analyzer at a refreshed prefix database.

Contribution Guide
------------------
1. Fork this repository.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Add tests that demonstrate the new behavior or fix.
4. Run the tests locally and ensure they pass.
5. Open a Pull Request describing the motivation and changes.

Coding standards:
- Write tests for bug fixes and new features.
- Keep changes small and focused.
- Use type hints where helpful.

Project Roadmap & Accuracy Notes
--------------------------------
This repository contains sample implementations that prioritize readability and testability over raw performance. For production:

- Replace in-memory linear-search structures with efficient indexes (radix tree, prefix trie, or database indices).
- Use authoritative data sources for GeoIP and ASN (update regularly and respect licensing).
- Harden network scanning code for platform-specific behavior and permissions.

Maintainer & Contact
--------------------
Maintainer: MrAmirRezaie
For questions, bug reports, or feature requests — open an Issue on the repository.

License
-------
This project is provided under the MIT License. See the `LICENSE` file for full terms.

Acknowledgements
----------------
This project was developed as an educational and practical toolkit demonstrating how small, testable network-analysis modules can be combined into a useful CLI-driven toolkit. Thank you to contributors and community reviewers.

---

If you want, I can also:
- Add a Persian translation section at the top of this README (bilingual file), or
- Create a separate `README.fa.md` with the Persian translation.

Tell me which you prefer and I will add it.
# IPAnalyzer — Completed

IPAnalyzer is a comprehensive IP analysis toolkit. This repository contains the final, completed state of the project: all roadmap phases and planned features have been implemented and finalized.

## Project Status


## Overview

IPAnalyzer provides a suite of IP-networking analysis tools including GeoIP lookup, BGP route inspection, bulk DNS processing, threat intelligence integration, GUI interfaces, persistent storage, and full IPv6 support. The project was carried through Phases 1–6 and consolidated into this final release.

## README — Complete Guide (English)

Welcome to IPAnalyzer — a modular toolkit for offline IP/network analysis. This README is a full guide: installation, architecture, usage (CLI and API), internal module descriptions, testing, and contribution guidelines.
- GeoIP Location Lookup (city, country, coordinates)
---
- BGP Route Information and AS path analysis
Table of Contents
- Overview
- Installation
- Quick Start (CLI)
- Python API Examples
- Modules and How They Work
- Data & Storage
- Testing
- Contributing
- License & Contact
- DNS Bulk Processor with concurrent resolution
---

Overview
--------
IPAnalyzer is designed to provide a set of independent, importable modules for analyzing IP addresses and networks without requiring external APIs. Typical features included in this codebase:

- GeoIP lookups using a small local CSV or in-memory DB
- BGP prefix table matching and ASN lookup
- Threat intelligence using local blacklist files
- Bulk DNS processing utilities
- WHOIS lookup and parsing helpers
- CLI wrapper to access core functionality

Design Principles
- Small, well-scoped modules (found under `ipanalyzer/modules/`).
- Minimal external dependencies — core functionality uses the Python standard library.
- Test-first approach: unit tests are in the `tests/` and top-level test files.

Installation
------------
Prerequisites:
- Python 3.8+

Recommended (create a virtual environment):

Windows (PowerShell):
```powershell
git clone https://github.com/MrAmirRezaie/IPAnalyzer.git
cd IPAnalyzer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # if the file exists
```

macOS / Linux:
```bash
git clone https://github.com/MrAmirRezaie/IPAnalyzer.git
cd IPAnalyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # if the file exists
```

If there are no external requirements, you can run modules directly with the venv Python.

Quick Start — CLI
-----------------
The repository includes a CLI entrypoint `ipanalyzer_cli.py` that wraps common operations. Run help to see available commands:

```bash
python ipanalyzer_cli.py --help
```

Common examples:

- GeoIP lookup
```bash
python ipanalyzer_cli.py geoip 8.8.8.8
```

- WHOIS lookup
```bash
python ipanalyzer_cli.py whois 8.8.8.8
```

- Batch processing
```bash
python ipanalyzer_cli.py batch ips.txt -o reports/batch.html
```

Python API — Usage Examples
---------------------------
Import and use modules directly from `ipanalyzer.modules`.

GeoIP lookup:

```python
from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer

geo = GeoIPAnalyzer()
result = geo.analyze('8.8.8.8')
print(result)
```

BGP (ASN) lookup:

```python
from ipanalyzer.modules.bgp_analyzer import BGPAnalyzer

b = BGPAnalyzer()
print(b.analyze_ip('8.8.8.8'))
```

Threat Intelligence (local blacklist):

```python
from ipanalyzer.modules.threat_intelligence import ThreatIntelligence

ti = ThreatIntelligence()
print(ti.analyze_threat('192.0.2.1'))
```

How the Core Modules Work
-------------------------
This section explains the architecture and internals of the most important modules. Each module is implemented to be usable on its own and expose a small, stable API.

1) GeoIP Analyzer (`ipanalyzer/modules/geoip_analyzer.py`)
- Purpose: Map IP to geographic metadata using a lightweight offline DB.
- Data: A small CSV shipped in `ipanalyzer/data/geoip_db.csv` or a built-in fallback table.
- Key methods: `analyze(ip) -> dict`, `batch_lookup(list_of_ips) -> list`, `clear_cache()`.
- Implementation details: Stores db as list of tuples (start_int, end_int, meta). Uses `ipaddress` to parse networks and linear search (suitable for a small DB). Summarizes ranges with `ipaddress.summarize_address_range` when returning CIDRs.

2) BGP Analyzer (`ipanalyzer/modules/bgp_analyzer.py`)
- Purpose: Provide offline mapping from IP to ASN and AS name using a small prefix table.
- Data: `_SAMPLE_PREFIXES` list of (start_int, end_int, asn, name) and `_AS_INFO_DB` with metadata.
- Key methods: `analyze_ip(ip)`, `get_asn_for_ip(ip)`, `get_as_info(asn)`, `find_origin(prefix)`, `trace_as_path(ip)`.
- Implementation details: Linear lookup in prefix table; returns a minimal AS path as a list (offline approximation). Caches results in-memory.

3) Threat Intelligence (`ipanalyzer/modules/threat_intelligence.py`)
- Purpose: Simple reputation engine based on local blacklist and a small in-memory threat DB.
- Data: Local blacklist file (plain text, one IP per line) and a small internal `_threat_db` map.
- Key methods: `analyze_threat(ip)`, `get_threat_history(ip)`, `add_to_blacklist(ip)`, `get_high_risk_ips(list_of_ips)`.
- Implementation details: Produces structured threat records with `last_seen` timestamps. Uses timezone-aware datetimes.

4) Other modules
- `ip_utils.py` provides helpers for IP/CIDR validation and conversion.
- `whois_analyzer.py` provides a simple WHOIS parsing helper (offline fallback + socket WHOIS queries).
- `report_generator.py` formats results into HTML/JSON reports.

Data & Storage
--------------
- `ipanalyzer/data/` contains small local data files such as `geoip_db.csv` and `blacklist.txt` used by modules.
- The project is designed to work offline with local data. For larger datasets, you can replace the in-memory DB with a small SQLite or other persistent store.

Testing
-------
Unit tests are provided. To run the full test suite from the project's root using the virtual environment Python:

```bash
.venv\Scripts\python -m pytest -q
```

If `pytest` is not available, install it into the venv first: `pip install pytest`.

Contribution Guide
------------------
1. Fork the repository
2. Create a feature branch (e.g., `feature/geoip-update`)
3. Write tests for your change
4. Run tests locally
5. Submit a pull request describing the change and linking any issues

Coding Guidelines
- Keep functions small and testable
- Add unit tests for new features and bug fixes
- Use type hints when convenient and maintain consistent style

Security and Privacy
--------------------
- IPAnalyzer is designed to run offline using local data files by default. No telemetry or remote calls are made unless explicitly invoked by the caller (e.g., online WHOIS or external lookups).

License
-------
This project is licensed under the MIT License — see the `LICENSE` file for details.

Maintainer & Contact
--------------------
Maintainer: MrAmirRezaie
For bugs and feature requests: open an Issue on the GitHub repository.
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
