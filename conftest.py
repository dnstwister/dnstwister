""" Test setup."""
import sys

import flask_webtest
import httpretty
import pytest

import dnstwister


# Add dnstwister to import path
sys.path.insert(0, 'dnstwister')


@pytest.fixture
def webapp():
    """Create a webapp fixture for accessing the site.

    Just include 'webapp' as an argument to the test method to use.
    """
    # Create a webtest Test App for use
    testapp = flask_webtest.TestApp(dnstwister.app)
    testapp.app.debug = True

    # Clear the cache
    dnstwister.cache.clear()

    return testapp


@pytest.yield_fixture
def f_httpretty():
    """httpretty doesn't work with pytest fixtures in python 2..."""
    httpretty.enable()
    httpretty.HTTPretty.allow_net_connect = False
    yield httpretty
    httpretty.disable()
    httpretty.reset()
