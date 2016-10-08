"""Tests of the domain suggester."""
import dnstwister.tools as tools


def test_suggestions_from_brands():

    assert tools.suggest_from({'domains': 'Voltswagen AG'}) == [
        'vag.com', 'voltswagen-ag.com', 'voltswagen.ag.com'
    ]

    assert tools.suggest_from({'domains': 'newlogic'}) == [
        'newlogic.com'
    ]
