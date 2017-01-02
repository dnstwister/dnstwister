"""View models for rendering the email template."""
import collections


class EmailReport(object):
    """View model for the email template."""
    def __init__(self, new, updated, deleted, noisy):
        self._new = new
        self._updated = updated
        self._deleted = deleted
        self._noisy = noisy

    @property
    def alertable(self):
        """Return the non-noisy results we want to alert on."""
        filtered = collections.defaultdict(None)
        if self._new is not None:
            filtered['new'] = [record
                               for record
                               in self._new
                               if record[0] not in self._noisy]

        if self._updated is not None:
            filtered['updated'] = [record
                                   for record
                                   in self._updated
                                   if record[0] not in self._noisy]

        if self._deleted is not None:
            filtered['deleted'] = [domain
                                   for domain
                                   in self._deleted
                                   if domain not in self._noisy]

        # Return None if no results in any operation.
        if sum(map(len, filtered.values())) == 0:
            return None

        return filtered

    @property
    def noisy(self):
        """Return the noisy results."""
        filtered = collections.defaultdict(None)
        if self._new is not None:
            filtered['new'] = [record
                               for record
                               in self._new
                               if record[0] in self._noisy]

        if self._updated is not None:
            filtered['updated'] = [record
                                   for record
                                   in self._updated
                                   if record[0] in self._noisy]

        if self._deleted is not None:
            filtered['deleted'] = [domain
                                   for domain
                                   in self._deleted
                                   if domain in self._noisy]

        # Return None if no results in any operation.
        if sum(map(len, filtered.values())) == 0:
            return None

        return filtered
