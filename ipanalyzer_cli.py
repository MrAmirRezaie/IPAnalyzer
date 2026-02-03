"""Minimal CLI for the IPAnalyzer package."""
import argparse
import json
from ipanalyzer import GeoIPAnalyzer, BGPAnalyzer, DNSBulkProcessor, ThreatIntel, ReportGenerator


def whois_cmd(args):
    geo = GeoIPAnalyzer()
    ti = ThreatIntel()
    info = geo.lookup(args.ip)
    info['threat'] = ti.info(args.ip)
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print(info)
        if args.output:
            html = ReportGenerator().generate_html(info)
            ReportGenerator().save(html, args.output)


def bgp_cmd(args):
    b = BGPAnalyzer()
    print(b.get_asn_for_ip(args.ip))


def dns_bulk_cmd(args):
    proc = DNSBulkProcessor()
    hosts = [h.strip() for h in args.hosts.split(',') if h.strip()]
    res = proc.bulk_resolve(hosts)
    print(res)


def main():
    p = argparse.ArgumentParser(prog='ipanalyzer')
    sub = p.add_subparsers(dest='cmd')

    w = sub.add_parser('whois')
    w.add_argument('ip')
    w.add_argument('--json', action='store_true')
    w.add_argument('-o', '--output')
    w.set_defaults(func=whois_cmd)

    b = sub.add_parser('bgp')
    b.add_argument('ip')
    b.set_defaults(func=bgp_cmd)

    d = sub.add_parser('dns-bulk')
    d.add_argument('hosts', help='comma separated hosts')
    d.set_defaults(func=dns_bulk_cmd)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()


if __name__ == '__main__':
    main()
"""
Main CLI Interface for IPAnalyzer
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from ipanalyzer import (
    WHOISAnalyzer,
    NetworkScanner,
    IPRangeAnalyzer,
    ReportGenerator,
    GeoIPAnalyzer,
    DNSBulkProcessor,
    BGPAnalyzer,
    ThreatIntelligence,
    DatabaseManager,
    PluginManager,
    IPAnalyzerGUI,
)
from ipanalyzer.modules.ip_utils import IPValidator


def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='IPAnalyzer - Advanced IP Analysis Tool',
        epilog='Created by MrAmirRezaie',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # WHOIS command
    whois_parser = subparsers.add_parser('whois', help='WHOIS lookup for IP address')
    whois_parser.add_argument('ip', help='IP address to analyze')
    whois_parser.add_argument('-o', '--output', help='Output HTML file')
    whois_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Network scan command
    scan_parser = subparsers.add_parser('scan', help='Scan network for connected devices')
    scan_parser.add_argument('--range', help='Network range (e.g., 192.168.1.0/24)')
    scan_parser.add_argument('-o', '--output', help='Output HTML file')
    scan_parser.add_argument('--json', action='store_true', help='Output as JSON')
    scan_parser.add_argument('--ports', help='Scan ports on discovered devices')
    
    # IP range analysis command
    range_parser = subparsers.add_parser('range', help='Analyze IP ranges and CIDR')
    range_parser.add_argument('cidr', help='CIDR notation (e.g., 192.168.1.0/24)')
    range_parser.add_argument('--subnet', type=int, help='Divide into subnets with prefix')
    range_parser.add_argument('--list-ips', action='store_true', help='List all IPs in range')
    range_parser.add_argument('--limit', type=int, default=1000, help='Limit IPs listed')
    range_parser.add_argument('-o', '--output', help='Output HTML file')
    range_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Port scan command
    port_parser = subparsers.add_parser('ports', help='Scan ports on a host')
    port_parser.add_argument('ip', help='IP address to scan')
    port_parser.add_argument('--ports', help='Comma-separated ports to scan')
    port_parser.add_argument('-o', '--output', help='Output HTML file')
    port_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Batch analysis command
    batch_parser = subparsers.add_parser('batch', help='Batch analyze multiple IPs')
    batch_parser.add_argument('file', help='File with IPs/CIDRs (one per line)')
    batch_parser.add_argument('-o', '--output', help='Output HTML file')
    batch_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # GeoIP command
    geoip_parser = subparsers.add_parser('geoip', help='GeoIP lookup (offline)')
    geoip_parser.add_argument('ip', nargs='?', help='IP address to lookup')
    geoip_parser.add_argument('--file', help='File with IPs (one per line)')

    # DNS bulk command
    dns_parser = subparsers.add_parser('dns', help='Bulk DNS processing')
    dns_group = dns_parser.add_mutually_exclusive_group(required=True)
    dns_group.add_argument('--forward', help='File with hostnames for forward lookup')
    dns_group.add_argument('--reverse', help='File with IPs for reverse lookup')
    dns_parser.add_argument('--threads', type=int, default=8, help='Number of threads')

    # BGP command
    bgp_parser = subparsers.add_parser('bgp', help='BGP route information (offline)')
    bgp_parser.add_argument('ip', help='IP address to analyze')

    # Threat intelligence
    threat_parser = subparsers.add_parser('threat', help='Threat intelligence lookup')
    threat_parser.add_argument('ip', nargs='?', help='IP address to check')

    # GUI
    gui_parser = subparsers.add_parser('gui', help='Launch GUI application')

    # Database management
    db_parser = subparsers.add_parser('db', help='Database storage operations')
    db_parser.add_argument('action', choices=['store', 'query'], help='Action')
    db_parser.add_argument('--file', help='File to store or import')
    db_parser.add_argument('--ip', help='IP to query')

    # Plugins
    plugins_parser = subparsers.add_parser('plugins', help='Plugin manager')
    plugins_parser.add_argument('--list', action='store_true', help='List available plugins')
    plugins_parser.add_argument('--exec', dest='exec', action='store_true', help='Execute a plugin')
    plugins_parser.add_argument('--plugin', help='Plugin name to execute')
    plugins_parser.add_argument('args', nargs='*', help='Arguments for plugin')
    
    return parser


def cmd_geoip(args):
    """Handle GeoIP lookup"""
    geo = GeoIPAnalyzer()
    if hasattr(args, 'ip') and args.ip:
        res = geo.analyze(args.ip)
        import json
        print(json.dumps(res, indent=2))
    elif hasattr(args, 'file') and args.file:
        res = geo.batch_analyze(open(args.file).read().splitlines())
        import json
        print(json.dumps(res, indent=2))


def cmd_dns(args):
    proc = DNSBulkProcessor(threads=getattr(args, 'threads', 8), timeout=5)
    if args.forward:
        res = proc.forward_lookup_batch(open(args.forward).read().splitlines())
        print(proc.export_results(res, format='csv'))
    elif args.reverse:
        res = proc.reverse_lookup_batch(open(args.reverse).read().splitlines())
        print(proc.export_results(res, format='csv'))


def cmd_bgp(args):
    analyzer = BGPAnalyzer()
    res = analyzer.analyze_ip(args.ip)
    import json
    print(json.dumps(res, indent=2))


def cmd_threat(args):
    ti = ThreatIntelligence()
    if args.ip:
        res = ti.analyze_threat(args.ip)
        import json
        print(json.dumps(res, indent=2))


def cmd_gui(args):
    gui = IPAnalyzerGUI()
    gui.run()


def cmd_db(args):
    db = DatabaseManager()
    if args.action == 'store' and args.file:
        # naive: store each line as a record
        with open(args.file, 'r', encoding='utf-8') as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                db.store_analysis('batch', {'ip': ln, 'raw': ln})
        print('Stored batch entries')
    elif args.action == 'query' and args.ip:
        res = db.query_history(args.ip)
        import json
        print(json.dumps(res, indent=2))


def cmd_plugins(args):
    mgr = PluginManager()
    if args.list:
        print('\n'.join(mgr.list_plugins()))
    elif args.exec and args.plugin:
        out = mgr.execute_plugin(args.plugin, *([] if not args.args else args.args))
        print(out)


def cmd_whois(args):
    """Handle WHOIS command"""
    if not IPValidator.is_valid_ipv4(args.ip):
        print(f"❌ Invalid IP address: {args.ip}")
        return
    
    print(f"🔍 Analyzing IP: {args.ip}")
    
    analyzer = WHOISAnalyzer()
    result = analyzer.analyze_ip(args.ip)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_whois_result(result)
    
    if args.output:
        generator = ReportGenerator()
        html = generator.generate_html_report(result, args.output)
        print(f"✅ Report saved to: {args.output}")


def cmd_scan(args):
    """Handle network scan command"""
    print("🔍 Scanning network...")
    
    scanner = NetworkScanner()
    network_info = scanner.get_network_info()
    
    print(f"📍 Local IP: {network_info.get('local_ip')}")
    print(f"🚪 Gateway: {network_info.get('gateway')}")
    
    network_range = args.range or network_info.get('estimated_range')
    if not network_range:
        print("❌ Could not determine network range. Please specify with --range")
        return
    
    print(f"📡 Scanning range: {network_range}")
    devices = scanner.scan_network(network_range)
    
    print(f"\n✅ Found {len(devices)} device(s)\n")
    
    result = {
        'network_info': network_info,
        'devices': devices,
        'scan_time': datetime.now().isoformat()
    }
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_devices_result(devices)
    
    if args.output:
        generator = ReportGenerator()
        html = generator.generate_html_report(result, args.output)
        print(f"\n✅ Report saved to: {args.output}")


def cmd_range(args):
    """Handle IP range analysis command"""
    if not IPValidator.is_valid_cidr(args.cidr):
        print(f"❌ Invalid CIDR notation: {args.cidr}")
        return
    
    print(f"📊 Analyzing range: {args.cidr}")
    
    analyzer = IPRangeAnalyzer()
    analysis = analyzer.analyze_cidr(args.cidr)
    
    result = {'ranges': [analysis]}
    
    if args.subnet:
        subnets = analyzer.subnet_division(args.cidr, args.subnet)
        result['ranges'] = [analyzer.analyze_cidr(subnet) for subnet in subnets]
        print(f"📑 Divided into {len(subnets)} subnets with /{args.subnet}\n")
    
    if args.list_ips:
        ips = analyzer.generate_ip_list(args.cidr, args.limit)
        print(f"📋 IPs in range (limited to {args.limit}):")
        for ip in ips:
            print(f"   {ip}")
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_range_result(result['ranges'])
    
    if args.output:
        generator = ReportGenerator()
        html = generator.generate_html_report(result, args.output)
        print(f"✅ Report saved to: {args.output}")


def cmd_ports(args):
    """Handle port scan command"""
    if not IPValidator.is_valid_ipv4(args.ip):
        print(f"❌ Invalid IP address: {args.ip}")
        return
    
    print(f"🔒 Scanning ports on: {args.ip}")
    
    scanner = NetworkScanner()
    
    ports = None
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
    
    open_ports = scanner.scan_ports(args.ip, ports)
    
    print(f"\n✅ Found {len(open_ports)} open port(s)\n")
    
    result = {
        'ip': args.ip,
        'open_ports': open_ports,
        'scan_time': datetime.now().isoformat()
    }
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_ports_result(args.ip, open_ports)
    
    if args.output:
        generator = ReportGenerator()
        html = generator.generate_html_report(result, args.output)
        print(f"\n✅ Report saved to: {args.output}")


def cmd_batch(args):
    """Handle batch analysis command"""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return
    
    print(f"📂 Reading IPs from: {args.file}")
    
    with open(args.file, 'r') as f:
        lines = f.read().strip().split('\n')
    
    print(f"📋 Found {len(lines)} entries\n")
    
    whois_analyzer = WHOISAnalyzer()
    range_analyzer = IPRangeAnalyzer()
    results = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '/' in line and IPValidator.is_valid_cidr(line):
            print(f"📊 Analyzing range: {line}")
            analysis = range_analyzer.analyze_cidr(line)
            results.append(analysis)
        elif IPValidator.is_valid_ipv4(line):
            print(f"🔍 Analyzing IP: {line}")
            analysis = whois_analyzer.analyze_ip(line)
            results.append(analysis)
        else:
            print(f"⚠️  Skipping invalid entry: {line}")
    
    print(f"\n✅ Analyzed {len(results)} entries\n")
    
    result = {
        'batch_results': results,
        'total_analyzed': len(results),
        'timestamp': datetime.now().isoformat()
    }
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        for r in results:
            print(f"Entry: {r}")
    
    if args.output:
        generator = ReportGenerator()
        html = generator.generate_html_report(result, args.output)
        print(f"✅ Report saved to: {args.output}")


def print_whois_result(result):
    """Print WHOIS result in readable format"""
    ip = result.get('ip')
    classification = result.get('classification')
    is_private = result.get('is_private')
    whois = result.get('whois', {})
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                    WHOIS ANALYSIS RESULT                   ║
╚════════════════════════════════════════════════════════════╝

IP Address:          {ip}
Classification:      {classification}
Private:             {'Yes' if is_private else 'No'}

Organization:        {whois.get('organization', 'N/A')}
Country:             {whois.get('country', 'N/A')}
Range:               {whois.get('range', 'N/A')}
RIR:                 {whois.get('rir', 'N/A')}
Source:              {whois.get('source', 'N/A')}

Timestamp:           {result.get('timestamp')}
""")


def print_devices_result(devices):
    """Print devices in readable format"""
    if not devices:
        print("No devices found.")
        return
    
    print("╔════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                          CONNECTED DEVICES                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════════════════╝\n")
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. IP: {device.get('ip', 'N/A')}")
        print(f"   MAC: {device.get('mac', 'N/A')}")
        print(f"   Hostname: {device.get('hostname', 'N/A')}")
        print(f"   Vendor: {device.get('vendor', 'N/A')}")
        print(f"   Status: {device.get('status', 'N/A')}")
        print()


def print_range_result(ranges):
    """Print IP range result in readable format"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    IP RANGE ANALYSIS                          ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    for r in ranges:
        print(f"CIDR:                {r.get('cidr')}")
        print(f"Network IP:          {r.get('network_ip')}")
        print(f"Broadcast IP:        {r.get('broadcast_ip')}")
        print(f"Netmask:             {r.get('netmask')}")
        print(f"Prefix Length:       /{r.get('prefix_length')}")
        print(f"IP Class:            {r.get('ip_class')}")
        print(f"Total Addresses:     {r.get('total_addresses')}")
        print(f"Usable Hosts:        {r.get('usable_hosts')}")
        print(f"First Usable IP:     {r.get('first_usable')}")
        print(f"Last Usable IP:      {r.get('last_usable')}")
        print()


def print_ports_result(ip, ports):
    """Print port scan result in readable format"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    PORT SCAN RESULT                           ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    print(f"Target IP: {ip}\n")
    
    if not ports:
        print("No open ports found.\n")
        return
    
    for port_info in ports:
        print(f"Port: {port_info.get('port')} ({port_info.get('service')})")
        print(f"Status: {port_info.get('status')}\n")


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    # Route to appropriate command handler
    commands = {
        'whois': cmd_whois,
        'scan': cmd_scan,
        'range': cmd_range,
        'ports': cmd_ports,
        'batch': cmd_batch,
        'geoip': cmd_geoip,
        'dns': cmd_dns,
        'bgp': cmd_bgp,
        'threat': cmd_threat,
        'gui': cmd_gui,
        'db': cmd_db,
        'plugins': cmd_plugins,
    }
    
    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
