"""Run-time feature flags."""
import os


def enable_noisy_domains():
    """Filter noisy domains out of emails and in to server-side report."""
    return os.getenv('feature.noisy_domains') == 'true'
