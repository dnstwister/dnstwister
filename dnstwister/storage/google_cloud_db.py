"""Google Cloud key-value datastore"""
from google.cloud import datastore
import zope.interface

from dnstwister.storage import interfaces


class GCDB(object):
    """Google Cloud database storage implementation."""
    zope.interface.implements(interfaces.IKeyValueDB)

    def __init__(self):
        self._client = datastore.Client()

    def ikeys(self, prefix):
        """Return an iterator of all the keys starting with a prefix,
        in the database.
        """
        query = self._client.query(kind=prefix)
        return query.keys_only()

    def set(self, prefix, key, value):
        """Insert/Update the value for a key."""
        entity = datastore.Entity(self._client.key(prefix, key))
        entity.update(value)
        self._client.put(entity)

    def delete(self, prefix, key):
        """Delete by key."""
        self._client.delete(self._client.key(prefix, key))

    def get(self, prefix, key):
        """Return the value for key, or None if no value."""
        return self._client.get(self._client.key(prefix, key))
