"""Run-time feature flags.

WARNING: these features require infrastructure beyond what is in this
repository.
"""
import os


def enable_noisy_domains():
    """Filter noisy domains out of emails and in to server-side report."""
    return os.getenv('feature.noisy_domains') == 'true'


def enable_async_search():
    """Enable the new, faster, async search."""
    return os.getenv('feature.async_search') == 'true'
