"""Storage implementations are expected to implement this interface."""
import zope.interface


class IKeyValueDB(zope.interface.Interface):
    """Interface for a key-value storage."""
    def set(self, prefix, key, value):
        """Set the value for key"""
        pass

    def get(self, key):
        """Get a value for key or None."""
        pass

    def ikeys(self, prefix=''):
        """Return an iterator of all keys, optionally filtered on prefix."""
        pass

    def delete(self, key):
        """Delete a key."""
        pass
