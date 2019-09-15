#pylint: skip-file
"""dnstwister web app.

This is the pattern from http://flask.pocoo.org/docs/0.11/patterns/packages/
which generates circular imports hence the comment at the top to just ignore
this file.
"""
import flask
import flask_caching
import logging

# Set up app/cache/db/emailer/gateway here
app = flask.Flask(__name__)
cache = flask_caching.Cache(app, config={'CACHE_TYPE': 'simple'})

# Logging
app.logger.setLevel(logging.INFO)

# Blueprints
import api
app.register_blueprint(api.app, url_prefix='/api')

# Import modules using dnstwister.app/cache/db/emailer here.
import tools
import tools.template
import views.www.analyse
import views.www.index
import views.www.search

# Filters
app.jinja_env.filters['domain_renderer'] = tools.template.domain_renderer
app.jinja_env.filters['domain_encoder'] = tools.template.domain_encoder
