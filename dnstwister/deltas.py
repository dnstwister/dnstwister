"""Delta report management."""
import datetime
import psycopg2

import main
db = main.db


REGISTER_UPDATE_DATE = datetime.datetime(1970, 1, 1)


def oldest(min_age=86400):
    """ Return the oldest delta that hasn't been updated for more than
    min_age.

    Return None if all deltas are up to date.

    min_age is in seconds, defaults to 24 hours.
    """
    age_delta = datetime.timedelta(seconds=min_age)
    domain, generated = db.deltas.oldest()
    age = datetime.datetime.now() - generated
    if age > age_delta:
        return domain

    print 'No domains to resolve for approx {} seconds'.format(
        int((age_delta - age).total_seconds())
    )


def update(domain, deltas, generated=None):
    """Update the delta for a domain.

    Args:
        domain: the domain (as string) being reported on
        new, updated, deleted: the delta info
        generated: when the report was generated. Defaults to now.
    """
    if generated is None:
        generated = datetime.datetime.now()
    db.deltas.set(domain, deltas, generated)


def get(domain):
    """Return the deltas for a domain, or None if one hasn't been created yet.
    """
    return db.deltas.get(domain)


def register(domain):
    """Add a domain to the deltas storage, with no CRUD data."""
    db.deltas.set(domain, None, REGISTER_UPDATE_DATE)


def registered(domain):
    """Check whether a domain is registered."""
    return db.deltas.exists(domain)
