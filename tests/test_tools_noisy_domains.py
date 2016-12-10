"""Tests of the tools.noisy_domains module."""
import datetime

from dnstwister.tools import noisy_domains


def test_initial_model():
    """Test how we set up a new domain."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    assert stats == {
        'domain': domain,
        'window_last_checked': now,
        'window_start': now,
        'deltas': 0,
    }


def test_update_when_inside_window():
    """Test we don't move the window inside the window_size."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=25))

    assert updated_stats == {
        'domain': stats['domain'],
        'window_last_checked': stats['window_last_checked'] + datetime.timedelta(days=25),
        'window_start': stats['window_start'],
        'deltas': stats['deltas'],
    }


def test_update_when_outside_window():
    """Test we move the window once we cross the threshold."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stats = noisy_domains.initialise_record(domain, now)

    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=31))

    assert updated_stats == {
        'domain': stats['domain'],
        'window_last_checked': stats['window_last_checked'] + datetime.timedelta(days=31),
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': stats['deltas'],
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
        'window_last_checked': stats['window_last_checked'] + datetime.timedelta(days=31),
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 5,
    }

    # The update to deltas is proportional to progress past the end of the
    # window, to highlight this we're pretending the update has ran more than
    # just 1 day after the window is crossed.
    stats['deltas'] = 16
    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=34))
    assert updated_stats == {
        'domain': stats['domain'],
        'window_last_checked': stats['window_last_checked'] + datetime.timedelta(days=34),
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 8,
    }

    stats['deltas'] = 24
    updated_stats = noisy_domains.update(stats, now + datetime.timedelta(days=45))
    assert updated_stats == {
        'domain': stats['domain'],
        'window_last_checked': stats['window_last_checked'] + datetime.timedelta(days=45),
        'window_start': stats['window_start'] + datetime.timedelta(days=15),
        'deltas': 16,
    }
