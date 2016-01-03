""" Run to build a static version of the index page. If not returning an error
    the index page can be 100% static. This makes it be ultra fast and free
    (bandwidth-wise).
"""
import jinja2
import os


os.chdir('dnstwister')

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join((
        os.path.dirname(__file__),
        'templates',
    ))),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

template = env.get_template('index.html')
with open('static/index_baked.html', 'wb') as htmlf:
    htmlf.write(template.render(error=None))
