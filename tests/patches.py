"""Mocks."""
class SimpleKVDatabase(object):
    """Replace the main storage with a lightweight in-memory shim."""

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        """Set the value for key"""
        self._data[key] = value

    def get(self, key):
        """Get a value for key or None."""
        try:
            return self._data[key]
        except KeyError:
            pass

    def ikeys(self, prefix=''):
        """Return an iterator of all keys, optionally filtered on prefix."""
        for key in self._data.keys():
            if key.startswith(prefix):
                yield key

    def delete(self, key):
        """Delete a key."""
        try:
            del self._data[key]
        except KeyError:
            pass
