"""Application repository."""
import main


class Repository(object):
    """Application repository to handle database activities."""

    def register_domain(self, domain):
        """Register a new domain for reporting.

        If the domain is already registered this is a no-op.
        """


    def oldest_updated(self, threshold=86400):
        """Return the domain with the oldest update date beyond threshold.

        Returns None if no domain's updated date is beyond the threshold.
        """


    def oldest_atom_read(self, threshold=86400):
        """Return the domain with the oldest last-read date beyond threshold.

        Returns None if no domain's last-read date is beyond the threshold.

        Used to identify domains to unregister.
        """


    def unregister(self, domain):
        """Unregisters a domain from reporting.

        Unregistering a domain that isn't registered is a no-op.
        """
