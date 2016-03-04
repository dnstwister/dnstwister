"""Storage implementations are expected to implement this interface."""
import zope.interface


class IReports(zope.interface.Interface):
    """Interface for the resolution reports implementation."""
    def set(self, domain, data, generated):
        """Insert/Update the resolution report for a domain."""
        pass

    def get(self, domain):
        """Return the resolution report for a domain, or None if no report."""
        pass


class IDeltas(zope.interface.Interface):
    """Interface for the deltas implementation."""
    def oldest(self):
        """Return the delta that hasn't been updated for the longest time.

        Returns (domain, generated_date) or None.
        """
        pass

    def set(self, domain, deltas, generated):
        """Insert/Update the delta for a domain."""
        pass

    def get(self, domain):
        """Return the delta report for a domain, or None if no delta."""
        pass
