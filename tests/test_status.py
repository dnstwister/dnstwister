"""Test of the status page."""
import json

import pytest
import webtest.app


def test_happy_status(f_httpretty, webapp, monkeypatch):
    """Test when it's all good."""
    dataclip_url = 'http://dnstwister.report/not_the_url.json'

    monkeypatch.setenv('MONITORING_DATACLIP', dataclip_url)

    payload = json.dumps({
        'fields':[
            'DNS resolution',
            'Atom feed delta generation',
            'Atom feed publishing',
            'Email subscription processing',
        ],
        'values':[[True, True, True, True]]
    })
    f_httpretty.register_uri(f_httpretty.GET, dataclip_url, body=payload)

    resp = webapp.get('/status')

    assert 'All systems operating normally' in resp.body


def test_degraded_status(f_httpretty, webapp, monkeypatch):
    """Test when we're having some issues."""
    dataclip_url = 'http://dnstwister.report/not_the_url.json'

    monkeypatch.setenv('MONITORING_DATACLIP', dataclip_url)

    payload = json.dumps({
        'fields':[
            'DNS resolution',
            'Atom feed delta generation',
            'Atom feed publishing',
            'Email subscription processing',
        ],
        'values':[[True, False, True, True]]
    })
    f_httpretty.register_uri(f_httpretty.GET, dataclip_url, body=payload)

    resp = webapp.get('/status')

    assert 'One or more issues detected' in resp.body


def test_no_dataclip(f_httpretty, webapp, monkeypatch):
    """Test when we can't talk to the dataclip we get a 500."""
    dataclip_url = 'http://dnstwister.report/not_the_url.json'

    monkeypatch.setenv('MONITORING_DATACLIP', dataclip_url)

    f_httpretty.register_uri(f_httpretty.GET, dataclip_url, status=404)

    with pytest.raises(webtest.app.AppError) as err:
        webapp.get('/status')
    assert '500 INTERNAL SERVER ERROR' in err.value.message
