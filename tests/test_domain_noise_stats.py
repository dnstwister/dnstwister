"""Tests of the noise statistics domain."""
import datetime

from dnstwister.domain.statistics import NoiseStatistic


def test_initialising_model():
    """Test how we set up a new statistic."""
    domain = 'www.example.com'
    now = datetime.datetime.now()

    stat = NoiseStatistic(domain, window_start=now)

    assert stat.domain == domain
    assert stat.window_start == now
    assert stat.deltas == 0
    assert stat.is_noisy is False


def test_initialising_model_with_custom_start():
    """Test how we set up a new statistic, pre-loading the hits."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    stat = NoiseStatistic(domain, deltas=1, window_start=now)

    assert stat.deltas == 1


def test_update_when_inside_window():
    """Test we don't move the window inside the window_size."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    future_date = now + datetime.timedelta(days=25)

    stat = NoiseStatistic(domain, window_start=now)
    stat.update_window(now=future_date)

    assert stat.window_start == now


def test_update_when_outside_window():
    """Test we move the window once we cross the threshold."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    future_date = now + datetime.timedelta(days=31)

    stat = NoiseStatistic(domain, window_start=now)
    stat.update_window(now=future_date)

    assert stat.window_start == now + datetime.timedelta(days=15)


def test_update_when_outside_window_updates_deltas():
    """Test we proportionally update the stats when we move a window."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    future_date = now + datetime.timedelta(days=31)

    stat = NoiseStatistic(domain, deltas=10, window_start=now)
    stat.update_window(now=future_date)

    assert stat.deltas == 5

    # The update to deltas is proportional to progress past the end of the
    # window, to highlight this we're pretending the update has ran more than
    # just 1 day after the window is crossed.
    stat = NoiseStatistic(domain, deltas=16, window_start=now)

    future_date = now + datetime.timedelta(days=34)
    stat.update_window(now=future_date)

    assert stat.deltas == 8

    stat = NoiseStatistic(domain, deltas=24, window_start=now)

    future_date = now + datetime.timedelta(days=45)
    stat.update_window(now=future_date)

    assert stat.deltas == 16


def test_increment():
    """Test the incrementing of a stats payload."""
    domain = 'www.example.com'
    stat = NoiseStatistic(domain)

    for _ in range(10):
        stat.increment()

    assert stat.deltas == 10


def test_delta_rate_needs_min_days():
    """Test the delta rate calculation needs 5 days of data to calc."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    past_date = now + datetime.timedelta(days=-3)
    stat = NoiseStatistic(domain, 10, window_start=past_date)

    assert stat.delta_rate == 0


def test_delta_rate_calculation():
    """Test the delta rate calculation."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    past_date = now + datetime.timedelta(days=-11)
    stat = NoiseStatistic(domain, 10, window_start=past_date)

    assert round(stat.delta_rate, 2) == 0.91


def test_noisy_flag_is_stable():
    """Test the noise flag itself."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    past_date = now + datetime.timedelta(days=-11)
    stat = NoiseStatistic(domain, 10, window_start=past_date)

    assert stat.is_noisy is True
    assert stat.is_noisy is True


def test_noisy_flag_on_threshold():
    """Test the noise flag triggers at the right threshold."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    past_date = now + datetime.timedelta(days=-10)
    stat = NoiseStatistic(domain, 5, window_start=past_date)

    assert stat.is_noisy is False
    assert stat.is_noisy is False

    stat = NoiseStatistic(domain, 6, window_start=past_date, noisy=False)

    assert stat.is_noisy is True
    assert stat.is_noisy is True

    stat = NoiseStatistic(domain, 5, window_start=past_date, noisy=True)

    assert stat.is_noisy is True
    assert stat.is_noisy is True


def test_noisy_flag_off_threshold():
    """Test the noise flag triggers at the right threshold."""
    domain = 'www.example.com'
    now = datetime.datetime.now()
    past_date = now + datetime.timedelta(days=-10)
    stat = NoiseStatistic(domain, 6, window_start=past_date)

    assert stat.is_noisy is True
    assert stat.is_noisy is True

    stat = NoiseStatistic(domain, 3, window_start=past_date, noisy=True)

    assert stat.is_noisy is True
    assert stat.is_noisy is True

    stat = NoiseStatistic(domain, 2, window_start=past_date, noisy=True)

    assert stat.is_noisy is False
    assert stat.is_noisy is False

    stat = NoiseStatistic(domain, 3, window_start=past_date, noisy=False)

    assert stat.is_noisy is False
    assert stat.is_noisy is False
