import datetime

import idna

import dnstwister.dnstwist.dnstwist as dnstwist


def test_long_request_does_not_timeout(webapp):
    """A particular long request was timing out in Production.

    domain.encode('idna') is 40x faster than idna.encode(domain)

    """
    return

    domain = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'

    tests = 50000

    start = datetime.datetime.now()

    for i in range(tests):
#        idna.encode(domain)
        domain.encode('idna')

    first = (datetime.datetime.now() - start).total_seconds()

    start = datetime.datetime.now()

    for i in range(tests):
#        domain.encode('idna')
        idna.encode(domain)

    second = (datetime.datetime.now() - start).total_seconds()

    assert [first, second] == []


def test2():
    """test2"""
    domain = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'

    start = datetime.datetime.now()

    dnstwist.fuzz_domain(domain)

    duration = (datetime.datetime.now() - start).total_seconds()

    assert duration == 2
