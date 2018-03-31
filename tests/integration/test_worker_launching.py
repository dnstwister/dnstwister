"""Tests of executing the workers as modules."""
import runpy

import pytest


def test_launching_stats_worker(monkeypatch):
    """We're happy for this to fail, but we just want to prove it's module-
    launchable.

    This simulates:

        python -m dnstwister.workers.stats

    """
    monkeypatch.delenv('DELTAS_URL', raising=False)

    with pytest.raises(Exception) as ex:
        runpy.run_module('dnstwister.workers.stats', run_name='__main__')

    assert ex.value.message == 'Delta report URL configuration not set!'


def test_launching_deltas_worker(monkeypatch):
    """We're happy for this to fail, but we just want to prove it's module-
    launchable.

    This simulates:

        python -m dnstwister.workers.deltas

    """
    monkeypatch.delenv('DATABASE_URL', raising=False)

    with pytest.raises(Exception) as ex:
        runpy.run_module('dnstwister.workers.deltas', run_name='__main__')

    assert ex.value.message == 'DATABASE_URL'


def test_launching_emails_worker(monkeypatch):
    """We're happy for this to fail, but we just want to prove it's module-
    launchable.

    This simulates:

        python -m dnstwister.workers.emails

    """
    monkeypatch.delenv('DATABASE_URL', raising=False)

    with pytest.raises(Exception) as ex:
        runpy.run_module('dnstwister.workers.email', run_name='__main__')

    assert ex.value.message == 'DATABASE_URL'
