"""Statistics models."""
import datetime


class NoiseStatistic(object):
    """Holds noise stats."""

    # How many days in a stats window.
    WINDOW_SIZE = 30

    # Higher and lower threshold to mark as noisy or not, of changes per day.
    NOISE_ON = 0.5
    NOISE_OFF = 0.25

    # Minimum number of days before returning a delta rate, to let the numbers
    # settle down.
    MIN_RATE_DAYS = 5

    def __init__(self, domain, deltas=0, window_start=None, noisy=False):
        if window_start is None:
            window_start = datetime.datetime.now()

        self._domain = domain
        self._deltas = deltas
        self._window_start = window_start
        self._noisy = noisy

    @property
    def domain(self):
        """This statistic's domain."""
        return self._domain

    @property
    def window_start(self):
        """The current window start date."""
        return self._window_start

    @property
    def deltas(self):
        """The number of deltas for this domain."""
        return self._deltas

    @property
    def is_noisy(self):
        """Are we a noisy domain?

        To prevent hunting there is an upper and lower bound to switch flag
        states, creating hysteresis.
        """
        new_flag = None

        if not self._noisy and self.delta_rate > self.NOISE_ON:
            new_flag = True
        elif self._noisy and self.delta_rate < self.NOISE_OFF:
            new_flag = False

        if new_flag is not None:
            self._noisy = new_flag

        return self._noisy

    @property
    def delta_rate(self):
        """Return the average number of deltas for a domain, per day."""
        window_age = (datetime.datetime.now() - self._window_start).days

        if window_age < self.MIN_RATE_DAYS:
            return 0

        return self._deltas / float(window_age)

    def update_window(self, now=None):
        """Update the window and (proportionally) the stats."""
        if now is None:
            now = datetime.datetime.now()

        window_age = now - self._window_start
        breakpoint = datetime.timedelta(days=self.WINDOW_SIZE)

        # Don't do anything to window if we're within the window.
        if window_age <= breakpoint:
            return

        # Shuffle the window half the window size if we're past the end.
        self._window_start += datetime.timedelta(days=self.WINDOW_SIZE / 2.0)

        # Work out what the deltas count would have been for this new
        # timespan. Take into account how far beyond the window end we are.
        delta_factor = 1 - ((self.WINDOW_SIZE / 2.0) / window_age.days)
        self._deltas = int(self._deltas * delta_factor)

    def increment(self):
        """Increment the number of deltas by 1."""
        self._deltas += 1
