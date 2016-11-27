"""Interface to the top-level-domains database in dnstwister.

It's small so we hold it in memory as a set.
"""
import codecs
import os


TLDS = set()

DB_PATH = os.path.join(
    'dnstwister',
    'dnstwist',
    'database',
    'effective_tld_names.dat'
)

if not os.path.exists(DB_PATH):
    raise Exception('TLD database is required!')

def valid_tld(line):
    """Return True if the line is a valid TLD, False otherwise."""
    line = line.strip()
    if line.startswith('//') or line.startswith('*') or line == '':
        return False
    try:
        codecs.decode(line, 'ascii')
    except TypeError:
        return False
    return True


with open(DB_PATH, 'rb') as tldf:
    TLDS.update(list(filter(valid_tld, str(tldf.read()).split('\n'))))
