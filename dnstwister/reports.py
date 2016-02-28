"""URL report management."""
import datetime


import main
db = main.db


def oldest(min_age=86400):
    """ Return the oldest URL that hasn't been updated for more than min_age.

    Return None if all reports are up to date.

    min_age is in seconds, defaults to 24 hours.
    """
    delta = datetime.timedelta(seconds=min_age)
    try:
        domain, updated = db.reports.oldest()
        if datetime.datetime.now() - updated > delta:
            return domain
    except TypeError:
        # No reports
        pass


def update(domain, report, updated=None):
    """Update the report for a domain.

    Args:
        domain: the domain (as string) being reported on
        report: the generated report (a dict)
        updated: when the report was updated. Defaults to now.
    """
    if updated is None:
        updated = datetime.datetime.now()
    db.reports.update(domain, report, updated)


def get(domain):
    """Return the report for a domain, or None if one hasn't been created yet.
    """
    return db.reports.get(domain)
