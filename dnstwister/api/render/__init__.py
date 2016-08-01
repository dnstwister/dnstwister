"""Page renderer"""
import base64
import io
import os
import subprocess
import warnings
import PIL.Image


warnings.simplefilter('error', PIL.Image.DecompressionBombWarning)

EXE = 'phantomjs'
MAX_DATA = 1024 * 1024  # 1MB
THUMB = (320, 240)


def thumbnail(image):
    """Reduce the size of the image to a suitable thumbnail."""
    p_image = PIL.Image.open(io.BytesIO(image))
    assert p_image.format == 'PNG'

    p_image.thumbnail(THUMB)

    thumb = io.BytesIO()
    p_image.save(thumb, format='png')

    return thumb.getvalue()


def render(domain):
    """Render a domain using PhantomJS, return the PNG data."""
    run_path = [
        EXE,
        os.path.join(os.path.dirname(__file__), 'render.js'),
        'http://{}'.format(domain)
    ]
    payload = subprocess.check_output(run_path)[:MAX_DATA]
    image = base64.b64decode(payload)
    image = thumbnail(image)
    return image
