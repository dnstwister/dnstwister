"""Page renderer"""
import base64
import os
import subprocess


EXE = 'phantomjs'


def render(domain):
    """Render a domain using PhantomJS, return the PNG data."""
    run_path = [
        EXE,
        os.path.join(os.path.dirname(__file__), 'render.js'),
        'http://{}'.format(domain)
    ]
    payload = subprocess.check_output(run_path)
    image = base64.b64decode(payload)
    return image
