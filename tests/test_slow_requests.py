import datetime

import dnstwister.tools


def test2():
    """Looooong domain names highlighted that the idna decoding is slooooow.

    This is a basic benchmark for performance.
    """
    domain = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'

    start = datetime.datetime.now()

    dnstwister.tools.fuzzy_domains(domain)

    duration = (datetime.datetime.now() - start).total_seconds()

    assert duration < 5, 'duration too long: {} secs'.format(duration)
