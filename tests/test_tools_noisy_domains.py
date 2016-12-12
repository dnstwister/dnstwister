"""Tests of the tools.noisy_domains module."""
import datetime

from dnstwister.tools import noisy_domains


def test_initialising_model():
    """Test how we set up a new domain."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    assert stats == {
        'domain': domain,
        'window_start': now,
        'deltas': 0,
        '__update': now,
        '__increment': now,
    }


def test_initialising_model_with_custom_start():
    """Test how we set up a new domain, pre-loading the hits."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now, start=1)

    assert stats == {
        'domain': domain,
        'window_start': now,
        'deltas': 1,
        '__update': now,
        '__increment': now,
    }


def test_update_when_inside_window():
    """Test we don't move the window inside the window_size."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=25))

    assert updated_stats == {
        'domain': stats['domain'],
        'window_start': stats['window_start'],
        'deltas': stats['deltas'],
        '__update': stats['__update'] + datetime.timedelta(days=25),
        '__increment': now,
    }


def test_update_when_outside_window():
    """Test we move the window once we cross the threshold."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=31))

    assert updated_stats == {
        'domain': stats['domain'],
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': stats['deltas'],
        '__update': stats['__update'] + datetime.timedelta(days=31),
        '__increment': now,
    }


def test_update_when_outside_window_updates_deltas():
    """Test we proportionally update the stats when we move a window."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    stats['deltas'] = 10
    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=31))
    assert updated_stats == {
        'domain': stats['domain'],
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 5,
        '__update': stats['__update'] + datetime.timedelta(days=31),
        '__increment': now,
    }

    # The update to deltas is proportional to progress past the end of the
    # window, to highlight this we're pretending the update has ran more than
    # just 1 day after the window is crossed.
    stats['deltas'] = 16
    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=34))
    assert updated_stats == {
        'domain': stats['domain'],
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 8,
        '__update': stats['__update'] + datetime.timedelta(days=34),
        '__increment': now,
    }

    stats['deltas'] = 24
    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=45))
    assert updated_stats == {
        'domain': stats['domain'],
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 16,
        '__update': stats['__update'] + datetime.timedelta(days=45),
        '__increment': now,
    }


def test_increment():
    """Test the incrementing of a stats payload."""
    now = datetime.datetime.now()
    domain = 'www.example.com'
    stats = noisy_domains.initialise_record(domain)

    date_cursor = now
    for _ in range(10):
        stats = noisy_domains.increment(stats, date_cursor)
        date_cursor += datetime.timedelta(days=1, minutes=1)

    # 9 because we call it immediately (time-wise) after initialising.
    assert stats['deltas'] == 9


def test_increment_is_max_once_per_day():
    """Test the incrementing of a stats payload."""
    now = datetime.datetime.now()

    domain = 'www.example.com'
    stats = noisy_domains.initialise_record(domain, now)

    date_cursor = now
    for _ in range(10):
        stats = noisy_domains.increment(stats, date_cursor)
        date_cursor += datetime.timedelta(days=0.5)

    assert stats['deltas'] == 3
