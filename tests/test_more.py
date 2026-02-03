from ipanalyzer.modules.whois_analyzer import WHOISAnalyzer
from ipanalyzer.modules.ip_range_analyzer import IPRangeAnalyzer


def test_iprange():
    a = IPRangeAnalyzer()
    info = a.analyze_cidr('192.168.1.0/24')
    assert info['total_addresses'] == 256
    subs = a.subnet_division('192.168.0.0/16', 24)
    assert '192.168.0.0/24' in subs


def test_whois_format():
    w = WHOISAnalyzer()
    r = w.lookup('8.8.8.8')
    assert 'ip' in r and r['ip'] == '8.8.8.8'
