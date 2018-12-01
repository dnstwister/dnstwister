import datetime

import dnstwister.tools


def test2():
    """test2"""
    domain = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'

    start = datetime.datetime.now()

    dnstwister.tools.fuzzy_domains(domain)

    duration = (datetime.datetime.now() - start).total_seconds()

    assert duration == 2
