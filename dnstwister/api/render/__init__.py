"""Page renderer"""
import os
import subprocess


EXE = 'phantomjs'


def render(domain):
    """Render a domain using PhantomJS."""
    run_path = [
        EXE,
        os.path.join(os.path.dirname(__file__), 'render.js'),
        'http://{}'.format(domain)
    ]
    print run_path
    return subprocess.check_output(run_path)
