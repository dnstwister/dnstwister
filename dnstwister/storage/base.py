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
    def update(self, domain, data, updated):
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
