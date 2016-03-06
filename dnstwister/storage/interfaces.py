"""Storage implementations are expected to implement this interface."""
import zope.interface.verify


class IKeyValueDB(zope.interface.Interface):
    """Interface for a key-value storage."""
    def set(self, key, value):
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


def instance_valid(instance):
    """Check an instance correctly implements storage."""
    return zope.interface.verify.verifyObject(IKeyValueDB, instance)
