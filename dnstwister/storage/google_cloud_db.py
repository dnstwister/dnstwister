"""Google Cloud key-value datastore"""
from google.cloud import datastore
import zope.interface

from dnstwister.storage import interfaces


class GCDB(object):
    """Google Cloud database storage implementation."""
    zope.interface.implements(interfaces.IKeyValueDB)

    def __init__(self):
        self._client = datastore.Client()

    def ikeys(self, kind):
        """Return an iterator of all the keys of a kind."""
        query = self._client.query(kind=kind)
        return query.keys_only()

    def set(self, kind, key, value):
        """Insert/Update the value for a key."""
        entity = datastore.Entity(self._client.key(kind, key))
        entity.update(value)
        self._client.put(entity)

    def delete(self, kind, key):
        """Delete by key."""
        self._client.delete(self._client.key(kind, key))

    def get(self, kind, key):
        """Return the value for key, or None if no value."""
        return self._client.get(self._client.key(kind, key))

    @staticmethod
    def to_db_datetime(datetime_obj):
        """Convert a datetime object to db datetime data.

        No conversion needed in google db.
        """
        return datetime_obj

    @staticmethod
    def from_db_datetime(datetime_data):
        """Convert datetime data from db to a datetime object.

        No conversion needed in google db.
        """
        return datetime_data
