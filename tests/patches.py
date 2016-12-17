"""Mocks."""


class NoEmailer(object):
    """Silent emailer."""
    def __init__(self, *args, **kwargs):
        self._emails = []

    @property
    def sent_emails(self):
        return list(self._emails)

    def send(self, *args):
        self._emails.append(args)


class SimpleKVDatabase(object):
    """Replace the main storage with a lightweight in-memory shim."""

    datetime_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self):
        self._data = {}

    @property
    def data(self):
        """Return a read-only dict representation of the data, for testing."""
        return dict(self._data)

    def set(self, prefix, key, value):
        """Set the value for key"""
        self._data[prefix + ':' + key] = value

    def get(self, prefix, key):
        """Get a value for key or None."""
        try:
            return self._data[prefix + ':' + key]
        except KeyError:
            pass

    def ikeys(self, prefix):
        """Return an iterator of all keys, optionally filtered on prefix."""
        for key in self._data.keys():
            if key.startswith(prefix + ':'):
                yield key.split(prefix + ':')[1]

    def delete(self, prefix, key):
        """Delete a key."""
        try:
            del self._data[prefix + ':' + key]
        except KeyError:
            pass


class SimpleFuzzer(object):
    """Replace the fuzzer with something that returns not much."""
    def __init__(self, domain):
        self._domain = domain

    def fuzz(self):
        pass

    @property
    def domains(self):
        return [
            {'domain-name': self._domain, 'fuzzer': 'Original*'},
            {'domain-name': self._domain[:-1], 'fuzzer': 'Pretend'},
        ]


class NoFuzzer(object):
    """Replace the fuzzer with something that returns nothing but the
    original domain."""
    def __init__(self, domain):
        self._domain = domain

    def fuzz(self):
        pass

    @property
    def domains(self):
        return [
            {'domain-name': self._domain, 'fuzzer': 'Original*'},
        ]
