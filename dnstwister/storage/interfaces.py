"""Storage implementations are expected to implement this interface."""
import zope.interface.verify


# pylint: disable=inherit-non-class,no-self-argument
class IKeyValueDB(zope.interface.Interface):
    """Interface for a key-value storage."""

    def set(kind, key, value):
        """Set the value for kind:key."""

    # pylint: disable=arguments-differ,signature-differs
    def get(kind, key):
        """Get a value for kind + key or None."""

    def ikeys(kind):
        """Return an iterator of all keys, optionally filtered on kind."""

    def delete(kind, key):
        """Delete a key."""

    def to_db_datetime(datetime_obj):
        """Convert a datetime object to db datetime data."""

    def from_db_datetime(datetime_data):
        """Convert datetime data from db to a datetime object."""


def instance_valid(instance):
    """Check an instance correctly implements storage."""
    return zope.interface.verify.verifyObject(IKeyValueDB, instance)
