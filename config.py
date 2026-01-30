"""
IPAnalyzer Configuration
Author: MrAmirRezaie
"""

# Tool Information
TOOL_NAME = "IPAnalyzer"
VERSION = "1.0.0"
AUTHOR = "MrAmirRezaie"
LICENSE = "MIT"

# WHOIS Configuration
WHOIS_SERVERS = {
    'ARIN': 'whois.arin.net',      # North America
    'RIPE': 'whois.ripe.net',      # Europe, Middle East
    'APNIC': 'whois.apnic.net',    # Asia-Pacific
    'LACNIC': 'whois.lacnic.net',  # Latin America
    'AFNIC': 'whois.afnic.fr',     # Africa
}

# Timeout settings (in seconds)
WHOIS_TIMEOUT = 5
PING_TIMEOUT = 1
SOCKET_TIMEOUT = 5

# Network scanning
COMMON_PORTS = [22, 80, 443, 3389, 5900, 8080, 8443, 25, 53, 110, 143, 3306, 5432, 6379, 27017]

# Report settings
REPORT_TEMPLATE = "default"
OUTPUT_ENCODING = "utf-8"

# Display settings
COLORS_ENABLED = True
VERBOSE = False

# Batch processing
BATCH_SIZE = 50
MAX_THREADS = 4
