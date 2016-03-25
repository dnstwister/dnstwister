"""Lightweight whois client."""
import contextlib
import socket
import string


SOCKOPTS = (socket.AF_INET, socket.SOCK_STREAM)
MAX_RECV = 1024


def _pairs(response):
    """Split a whois response into key-value dict."""
    tokens = [map(string.strip, row.split(':', 1))
              for row
              in response.split('\n')]

    whois_pairs = dict([token
                       for token
                       in tokens
                       if len(token) == 2
                       and tokens[1] != ''])
    return whois_pairs


def _interact(server, query):
    """Interact with a whois server, returning the key-value pairs."""
    with contextlib.closing(socket.socket(*SOCKOPTS)) as s:
        s.settimeout(5)
        s.connect((server, 43))
        s.sendall('{}\r\n'.format(query.strip()))

        payload = ''
        while True:
            chunk = s.recv(MAX_RECV)
            payload += chunk
            if 'whois:' in chunk or chunk == '':
                break

        return payload


def lookup(domain, start_server='whois.iana.org', max_hops=5):
    """Perform a whois lookup, returning a dict or None on failure."""
    seen = set()
    hops = 0
    whois_server = start_server

    while True and hops < max_hops:

        if whois_server in seen:
            return

        whois_data = _interact(whois_server, domain)
        whois_pairs = _pairs(whois_data)

        seen.add(whois_server)
        hops += 1

        if any([key.startswith('Registrant') for key in whois_pairs.keys()]):
            return whois_data.strip()

        # Try to find a referrer whois server.
        try:
            whois_server = whois_pairs['whois']
            continue
        except KeyError:
            pass

        try:
            whois_server = whois_pairs['Whois Server']
            continue
        except KeyError:
            pass

        try:
            whois_server = [val
                            for val
                            in whois_pairs.values()
                            if val.startswith('whois.')][0]
            continue
        except IndexError:
            pass


if __name__ == '__main__':
    import sys
    print lookup(sys.argv[-1])
