"""Storage implementations are expected to implement this interface."""
import zope.interface.verify


# pylint: disable=inherit-non-class
class IKeyValueDB(zope.interface.Interface):
    """Interface for a key-value storage."""

    # pylint: disable=no-self-argument
    def set(kind, key, value):
        """Set the value for kind:key."""

    # pylint: disable=arguments-differ,signature-differs,no-self-argument
    def get(kind, key):
        """Get a value for kind + key or None."""

    # pylint: disable=no-self-argument
    def ikeys(kind):
        """Return an iterator of all keys, optionally filtered on kind."""

    # pylint: disable=no-self-argument
    def delete(kind, key):
        """Delete a key."""

    # pylint: disable=no-self-argument
    def to_db_datetime(datetime_obj):
        """Convert a datetime object to db datetime data."""

    # pylint: disable=no-self-argument
    def from_db_datetime(datetime_data):
        """Convert datetime data from db to a datetime object."""


def instance_valid(instance):
    """Check an instance correctly implements storage."""
    return zope.interface.verify.verifyObject(IKeyValueDB, instance)
