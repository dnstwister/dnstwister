"""Run-time feature flags.

WARNING: these features require infrastructure beyond what is in this
repository.

You are welcome to enable them yourself and try them out but I cannot support
issues found doing so.
"""
import os


def enable_noisy_domains():
    """Filter noisy domains out of emails and in to server-side report."""
    return os.getenv('feature.noisy_domains') == 'true'


def enable_async_search():
    """Enable the new, faster, async search."""
    return os.getenv('feature.async_search') == 'true'


def enable_emails():
    return os.getenv('feature.emails') == 'true'
