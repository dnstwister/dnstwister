"""Noisy domain tracking and identification.

We keep a sliding window of deltas per domain over time.
"""
import datetime


# Sliding window size
WINDOW_SIZE = 30

# How often to execute on stats records.
FREQUENCY = datetime.timedelta(days=1)

# Higher and lower threshold to mark as noisy or not, of changes per day.
NOISE_MIN_DAYS = 5
NOISE_ON = 0.5
NOISE_OFF = 0.25


def initialise_record(domain, now=None, start=0):
    """The initial values if there is no noise record for a domain."""
    if now is None:
        now = datetime.datetime.now()

    model = {
        'domain': domain,
        'window_start': now,
        'deltas': start,
        '__update': now,
        '__increment': now,
        'noisy': False,
    }
    return model


def limit_frequency(function):
    """Decorator to limit calls to function to FREQUENCY."""
    def wrapper(domain_stats, now=None):
        """Not using *ags and **kwargs as know signatures."""
        if now is None:
            now = datetime.datetime.now()

        domain_stats = dict(domain_stats)

        updated_key = '__{}'.format(function.func_name)
        if now - domain_stats[updated_key] <= FREQUENCY:
            return domain_stats

        domain_stats[updated_key] = now
        return function(domain_stats, now)

    return wrapper


@limit_frequency
def update(domain_stats, now=None):
    """Update the domain window, stats and noisiness.

    Shuffles the start date of the window for this delta forward by 1/2
    WINDOW_SIZE size once we're more than WINDOW_SIZE beyond when we last
    shuffled it forward. We update the hits proportionally in doing this.

    This gives a rough sliding window of values whilst only storing a start
    date for the window and current hits.
    """
    if now is None:
        now = datetime.datetime.now()

    # Work out if is noisy or not
    update_noisy_flag(domain_stats)

    window_start = domain_stats['window_start']
    window_age = now - window_start

    breakpoint = datetime.timedelta(days=WINDOW_SIZE)
    move_size = datetime.timedelta(days=WINDOW_SIZE / 2.0)

    # Don't do anything to window if we're within the window.
    if window_age <= breakpoint:
        return domain_stats

    # Shuffle the window half the window size if we're past the end.
    domain_stats['window_start'] = window_start + move_size

    # Work out what the deltas count would have been for this new timespan.
    # Take into account how far beyond the window we are.
    delta_factor = 1 - ((WINDOW_SIZE / 2.0) / window_age.days)

    domain_stats['deltas'] = int(domain_stats['deltas'] * delta_factor)

    return domain_stats


@limit_frequency
def increment(domain_stats, now=None):
    """Increment the number of deltas in the stats, return them."""
    if now is None:
        now = datetime.datetime.now()
    domain_stats['deltas'] += 1
    return domain_stats


def update_noisy_flag(domain_stats):
    """Update the noisiness flag based on current state and delta rate."""
    currently_noisy = domain_stats['noisy']
    if not currently_noisy and delta_rate(domain_stats) > NOISE_ON:
        domain_stats['noisy'] = True
    elif currently_noisy and delta_rate(domain_stats) < NOISE_OFF:
        domain_stats['noisy'] = False

def delta_rate(domain_stats, min_days=5, now=None):
    """Return the average number of deltas for a domain, per day.

    min_days ensures we don't get too sensitive readings early on.
    """
    if now is None:
        now = datetime.datetime.now()

    window_start = domain_stats['window_start']
    window_age = now - window_start

    if window_age.days <= min_days:
        return 0

    return domain_stats['deltas'] / float(window_age.days)
