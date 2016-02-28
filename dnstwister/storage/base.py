"""Storage implementations are expected to register against this ABC."""
import abc


class Reports(object):
    """ABC for the reports implementation.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def oldest(self):
        """Return the domain that hasn't been checked for the longest time.

        Returns (domain, update_date) or None.
        """
        pass

    @abc.abstractmethod
    def update(self, domain, data, generated):
        """Update the latest result for a domain."""
        pass

    @abc.abstractmethod
    def new(self, domain, start_date):
        """Create a new entry with no report.

        By using a date in the past you can push the report to the top of the
        queue.
        """
        pass

    @abc.abstractmethod
    def get(self, domain):
        """Return the report for a domain, or None if no domain."""
        pass


class Deltas(object):
    """ABC for the deltas implementation.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def oldest(self):
        """Return the delta that hasn't been updated for the longest time.

        Returns (domain, generated_date) or None.
        """
        pass

    @abc.abstractmethod
    def set(self, domain, deltas, generated):
        """Add/update the delta for a domain."""
        pass

    @abc.abstractmethod
    def get(self, domain):
        """Return the delta info for a domain, or None if no delta."""
        pass

    @abc.abstractmethod
    def exists(self, domain):
        """Return whether a delta exists (domains or not) in the database."""
        pass

    @abc.abstractmethod
    def updated(self, domain):
        """Return the update date for a delta, or None."""
        pass
