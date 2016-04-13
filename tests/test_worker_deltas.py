"""Tests of the deltas worker."""
import dnstwister
import patches
import worker_deltas


def test_invalid_domain_is_unregistered(capsys, monkeypatch):
    """Invalid domains are tidied up."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    repository = dnstwister.repository

    invalid_domain = '3j88??ASd'
    assert not repository.is_domain_registered(invalid_domain)

    repository.register_domain(invalid_domain)
    assert repository.is_domain_registered(invalid_domain)

    worker_deltas.process_domain(invalid_domain)
    assert not repository.is_domain_registered(invalid_domain)

    expected_output = 'Unregistering (invalid) {}\n'.format(invalid_domain)
    assert capsys.readouterr()[0] == expected_output

