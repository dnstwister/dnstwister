"""Mocks."""


class DeltasDB(object):
    """Replace the main storage with a lightweight in-memory shim."""
    def __init__(self):
        self._db = {}

    def get(self, domain):
        try:
            return self._db[domain][0]
        except KeyError:
            pass

    def exists(self, domain):
        return domain in self._db.keys()

    def set(self, domain, delta, generated):
        self._db[domain] = (delta, generated)

    def reset(self):
        self._db = {}


deltas = DeltasDB()
