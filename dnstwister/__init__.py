#pylint: skip-file
"""dnstwister web app.

This is the pattern from http://flask.pocoo.org/docs/0.11/patterns/packages/
which generates circular imports hence the comment at the top to just ignore
this file.
"""
import flask
import logging

app = flask.Flask(__name__)

# Logging
app.logger.setLevel(logging.INFO)

# Blueprints
import dnstwister.api
app.register_blueprint(api.app, url_prefix='/api')

# Import modules using dnstwister.app
import dnstwister.tools.template
import dnstwister.views.www.analyse
import dnstwister.views.www.index
import dnstwister.views.www.search

# Filters
app.jinja_env.filters['domain_renderer'] = tools.template.domain_renderer
app.jinja_env.filters['domain_encoder'] = tools.template.domain_encoder
