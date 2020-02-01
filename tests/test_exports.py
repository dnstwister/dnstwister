"""Test the csv/json export functionality."""
import binascii
import textwrap

import dnstwister.tools
import patches
from dnstwister.core.domain import Domain


def test_csv_export(webapp, monkeypatch):
    """Test CSV export"""
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = Domain('a.com')
    hexdomain = domain.to_hex()

    response = webapp.get('/search/{}/csv'.format(hexdomain))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_a.com.csv'

    assert '\n'.join(sorted(response.text.strip().split('\n'))) == textwrap.dedent("""
        Domain,Type,Tweak,IP,Error
        a.com,Addition,aa.com,999.999.999.999,False
        a.com,Addition,ab.com,999.999.999.999,False
        a.com,Addition,ac.com,999.999.999.999,False
        a.com,Addition,ad.com,999.999.999.999,False
        a.com,Addition,ae.com,999.999.999.999,False
        a.com,Addition,af.com,999.999.999.999,False
        a.com,Addition,ag.com,999.999.999.999,False
        a.com,Addition,ah.com,999.999.999.999,False
        a.com,Addition,ai.com,999.999.999.999,False
        a.com,Addition,aj.com,999.999.999.999,False
        a.com,Addition,ak.com,999.999.999.999,False
        a.com,Addition,al.com,999.999.999.999,False
        a.com,Addition,am.com,999.999.999.999,False
        a.com,Addition,an.com,999.999.999.999,False
        a.com,Addition,ao.com,999.999.999.999,False
        a.com,Addition,ap.com,999.999.999.999,False
        a.com,Addition,aq.com,999.999.999.999,False
        a.com,Addition,ar.com,999.999.999.999,False
        a.com,Addition,as.com,999.999.999.999,False
        a.com,Addition,at.com,999.999.999.999,False
        a.com,Addition,au.com,999.999.999.999,False
        a.com,Addition,av.com,999.999.999.999,False
        a.com,Addition,aw.com,999.999.999.999,False
        a.com,Addition,ax.com,999.999.999.999,False
        a.com,Addition,ay.com,999.999.999.999,False
        a.com,Addition,az.com,999.999.999.999,False
        a.com,Bitsquatting,c.com,999.999.999.999,False
        a.com,Bitsquatting,e.com,999.999.999.999,False
        a.com,Bitsquatting,i.com,999.999.999.999,False
        a.com,Bitsquatting,q.com,999.999.999.999,False
        a.com,Original*,a.com,999.999.999.999,False
        a.com,Replacement,1.com,999.999.999.999,False
        a.com,Replacement,2.com,999.999.999.999,False
        a.com,Replacement,s.com,999.999.999.999,False
        a.com,Replacement,w.com,999.999.999.999,False
        a.com,Replacement,y.com,999.999.999.999,False
        a.com,Replacement,z.com,999.999.999.999,False
        a.com,Various,acom.com,999.999.999.999,False
        a.com,Various,wwa.com,999.999.999.999,False
        a.com,Various,www-a.com,999.999.999.999,False
        a.com,Various,wwwa.com,999.999.999.999,False
        a.com,Vowel swap,o.com,999.999.999.999,False
        a.com,Vowel swap,u.com,999.999.999.999,False
    """).strip()


def test_json_export(webapp, monkeypatch):
    """Test JSON export"""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = Domain('a.com')
    path = domain.to_hex()

    response = webapp.get('/search/{}/json'.format(path))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_a.com.json'

    assert response.json == {
        u'a.com': {
            u'fuzzy_domains': [
                {
                    u'domain-name': u'a.com',
                    u'fuzzer': u'Original*',
                    u'hex': u'612e636f6d',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                },
                {
                    u'domain-name': u'a.co',
                    u'fuzzer': u'Pretend',
                    u'hex': u'612e636f',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                }
            ]
        }
    }


def test_json_export_one_domain(webapp, monkeypatch):
    """Test JSON export when no reports"""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domains = ('a.com',)
    path = ','.join([Domain(d).to_hex() for d in domains])

    response = webapp.get('/search/{}/json'.format(path))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_a.com.json'

    assert response.json == {
        u'a.com': {
            u'fuzzy_domains': [
                {
                    u'domain-name': u'a.com',
                    u'fuzzer': u'Original*',
                    u'hex': u'612e636f6d',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                },
                {
                    u'domain-name': u'a.co',
                    u'fuzzer': u'Pretend',
                    u'hex': u'612e636f',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                }
            ]
        }
    }


def test_json_export_no_fuzzy(webapp, monkeypatch):
    """Test JSON export when no fuzzy domains."""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.NoFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domains = ('a.com',)
    path = ','.join([Domain(d).to_hex() for d in domains])

    response = webapp.get('/search/{}/json'.format(path))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_a.com.json'

    assert response.json == {
        u'a.com': {
            u'fuzzy_domains': [
                {
                    u'domain-name': u'a.com',
                    u'fuzzer': u'Original*',
                    u'hex': u'612e636f6d',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                }
            ]
        }
    }


def test_json_export_formatting(webapp, monkeypatch):
    """Test JSON export looks nice :)"""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = 'a.com'
    path = Domain(domain).to_hex()

    response = webapp.get('/search/{}/json'.format(path))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_a.com.json'

    assert response.text.strip() == textwrap.dedent("""
        {
            "a.com": {
                "fuzzy_domains": [
                    {
                        "domain-name": "a.com",
                        "fuzzer": "Original*",
                        "hex": "612e636f6d",
                        "resolution": {
                            "error": false,
                            "ip": "999.999.999.999"
                        }
                    },
                    {
                        "domain-name": "a.co",
                        "fuzzer": "Pretend",
                        "hex": "612e636f",
                        "resolution": {
                            "error": false,
                            "ip": "999.999.999.999"
                        }
                    }
                ]
            }
        }
    """).strip()


def test_failed_export(webapp):
    """Test unknown-format export"""
    domain = 'a.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/search/{}/xlsx'.format(hexdomain), expect_errors=True)
    assert response.status_code == 400


def test_links_on_report(webapp):
    """Make sure the export links are working."""
    domain = Domain('a.com')
    hexdomain = domain.to_hex()
    page_html = webapp.get('/search/{}'.format(hexdomain)).text

    assert '/search/{}/csv'.format(hexdomain) in page_html
    assert '/search/{}/json'.format(hexdomain) in page_html


def test_json_export_unicode_domain(webapp, monkeypatch):
    """Test JSON export when no reports"""
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = u'a\u00E0.com'  # almost 'aa.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/search/{}/json'.format(hexdomain))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_xn--a-sfa.com.json'

    assert response.json == {
        u'xn--a-sfa.com': {
            u'fuzzy_domains': [
                {
                    u'domain-name': u'xn--a-sfa.com',
                    u'fuzzer': u'Original*',
                    u'hex': u'786e2d2d612d7366612e636f6d',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                },
                {
                    u'domain-name': u'xn--a-sfa.co',
                    u'fuzzer': u'Pretend',
                    u'hex': u'786e2d2d612d7366612e636f',
                    u'resolution': {
                        u'error': False,
                        u'ip': u'999.999.999.999'
                    }
                }
            ]
        }
    }


def test_unicode_csv_export(webapp, monkeypatch):
    """Test CSV export with Unicode"""
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )

    domain = u'a\u00E0.com'  # almost 'aa.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/search/{}/csv'.format(hexdomain))

    assert response.headers['Content-Disposition'] == 'attachment; filename=dnstwister_report_xn--a-sfa.com.csv'

    assert '\n'.join(sorted(response.text.strip().split('\n'))) == textwrap.dedent("""
        Domain,Type,Tweak,IP,Error
        xn--a-sfa.com,Addition,xn--aa-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ab-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ac-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ad-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ae-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--af-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ag-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ah-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ai-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--aj-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ak-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--al-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--am-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--an-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ao-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ap-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--aq-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ar-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--as-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--at-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--au-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--av-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--aw-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ax-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--ay-jia.com,999.999.999.999,False
        xn--a-sfa.com,Addition,xn--az-jia.com,999.999.999.999,False
        xn--a-sfa.com,Bitsquatting,xn--c-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Bitsquatting,xn--e-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Bitsquatting,xn--i-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Bitsquatting,xn--q-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca15e.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca3e.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca743m.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca76d.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca7e.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0ca98b.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0caa.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0cab.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0cad.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0caf.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0cah.com,999.999.999.999,False
        xn--a-sfa.com,Homoglyph,xn--0caj.com,999.999.999.999,False
        xn--a-sfa.com,Hyphenation,xn--a--kia.com,999.999.999.999,False
        xn--a-sfa.com,Omission,a.com,999.999.999.999,False
        xn--a-sfa.com,Omission,xn--0ca.com,999.999.999.999,False
        xn--a-sfa.com,Original*,xn--a-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Repetition,xn--a-sfaa.com,999.999.999.999,False
        xn--a-sfa.com,Repetition,xn--aa-kia.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--1-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--2-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--s-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--w-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--y-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Replacement,xn--z-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Subdomain,a.xn--0ca.com,999.999.999.999,False
        xn--a-sfa.com,Transposition,xn--a-rfa.com,999.999.999.999,False
        xn--a-sfa.com,Various,xn--acom-0na.com,999.999.999.999,False
        xn--a-sfa.com,Various,xn--wwa-cla.com,999.999.999.999,False
        xn--a-sfa.com,Various,xn--www-a-vqa.com,999.999.999.999,False
        xn--a-sfa.com,Various,xn--wwwa-3na.com,999.999.999.999,False
        xn--a-sfa.com,Vowel swap,xn--o-sfa.com,999.999.999.999,False
        xn--a-sfa.com,Vowel swap,xn--u-sfa.com,999.999.999.999,False
    """).strip()
