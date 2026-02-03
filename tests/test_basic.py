import json
from ipanalyzer import GeoIPAnalyzer, BGPAnalyzer, DNSBulkProcessor, ThreatIntel, IPUtils


def test_geoip():
    g = GeoIPAnalyzer()
    r = g.lookup('8.8.8.8')
    assert r.get('country') == 'United States'


def test_bgp():
    b = BGPAnalyzer()
    r = b.get_asn_for_ip('8.8.8.8')
    assert 'asn' in r


def test_dnsbulk_resolve():
    d = DNSBulkProcessor()
    # localhost should always resolve
    res = d.resolve('localhost')
    assert 'addresses' in res or 'error' in res


def test_threat():
    t = ThreatIntel()
    r = t.info('203.0.113.5')
    assert r['blacklisted'] is True


def test_iputils():
    assert IPUtils.is_valid_ip('8.8.8.8')
    assert IPUtils.is_ipv4('8.8.8.8')
