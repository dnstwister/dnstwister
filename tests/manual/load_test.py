# Manual test script to assist with load testing.
#
# Usage:
#           python load_test.py [endpoint]
#
# Eg:
#           python load_test.py http://localhost:5000/search/
#           python load_test.py http://localhost:5000/api/fuzz/
#           python load_test.py http://localhost:5000/api/fuzz_chunked/
#
import binascii
import datetime
import multiprocessing
import sys

import requests


DOMAIN_TEMPLATE = '{}zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'
CLIENTS = 50


def request(args):
    endpoint, domain = args
    url = '{}{}'.format(
        endpoint,
        binascii.hexlify(domain.encode('idna'))
    )

    start = datetime.datetime.now()
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print 'Failed {} with {}'.format(url, response.status_code)
        return
    generator = response.iter_content(chunk_size=None)
    content = next(generator)  # We're timing how long the first result took.
#    print content
    end = datetime.datetime.now()
    print '.',


def test(endpoint):
    start = datetime.datetime.now()
    pool = multiprocessing.Pool(CLIENTS)
    args = [(endpoint, DOMAIN_TEMPLATE.format(i))
            for i
            in range(CLIENTS)]
    pool.map(request, args)
    end = datetime.datetime.now()
    print '\n\n{} requests took {} seconds\n\n'.format(
        CLIENTS,
        (end - start).total_seconds()
    )


if __name__ == '__main__':
    endpoint = sys.argv[1]
    test(endpoint)
