"""Page renderer"""
import os
import subprocess


EXE = 'phantomjs.exe'

TEMPLATE = """
    var system = require('system');
    var args = system.args;
    var url = args[1];

    var page = require('webpage').create();
    page.viewportSize = {
      width: 800,
      height: 600,
    };
    page.clipRect = {
      top: 0,
      left: 0,
      width: 800,
      height: 600
    };
    page.open(url, function() {
      console.log(page.renderBase64('png'));
      phantom.exit();
    });
"""


def render(domain):
    """Render a domain using PhantomJS."""
    run_path = [
        os.path.join(os.path.dirname(__file__), EXE),
        os.path.join(os.path.dirname(__file__), 'test.js'),
        'http://{}'.format(domain)
    ]
    return subprocess.check_output(run_path)
