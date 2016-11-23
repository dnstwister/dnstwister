#pylint: skip-file
"""dnstwister web app.

This is the pattern from http://flask.pocoo.org/docs/0.11/patterns/packages/
which generates circular imports hence the comment at the top to just ignore
this file.
"""
import flask
import flask_cache
import logging

import dnstwister.mail.sendgridservice
import dnstwister.storage.pg_database


# Set up app/cache/db/emailer/gateway here
app = flask.Flask(__name__)
cache = flask_cache.Cache(app, config={'CACHE_TYPE': 'simple'})
db = storage.pg_database.PGDatabase()
emailer = mail.sendgridservice.SGSender()

# Logging
app.logger.setLevel(logging.INFO)

# Blueprints
from . import api
app.register_blueprint(api.app, url_prefix='/api')

# Import modules using dnstwister.app/cache/db/emailer here.
import dnstwister.repository
import dnstwister.tools
import dnstwister.views.syndication.atom
import dnstwister.views.www.analyse
import dnstwister.views.www.email
import dnstwister.views.www.help
import dnstwister.views.www.index
import dnstwister.views.www.search
import dnstwister.views.www.status
