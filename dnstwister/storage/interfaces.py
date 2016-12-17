"""Storage implementations are expected to implement this interface."""
import zope.interface.verify


# pylint: disable=inherit-non-class
class IKeyValueDB(zope.interface.Interface):
    """Interface for a key-value storage."""
    def set(self, prefix, key, value):
        """Set the value for prefix:key.
        """

    # pylint: disable=arguments-differ
    def get(self, prefix, key):
        """Get a value for prefix:key or None."""

    def ikeys(self, prefix):
        """Return an iterator of all keys, optionally filtered on prefix."""

    def delete(self, prefix, key):
        """Delete a key."""


def instance_valid(instance):
    """Check an instance correctly implements storage."""
    return zope.interface.verify.verifyObject(IKeyValueDB, instance)
