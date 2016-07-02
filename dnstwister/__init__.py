"""dnstwister web app."""
import flask
import flask.ext.cache
import logging

import mail.sendgridservice
import storage.pg_database


# Set up app/cache/db/emailer/gateway here
app = flask.Flask(__name__)
cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})
db = storage.pg_database.PGDatabase()
emailer = mail.sendgridservice.SGSender()


# Logging
@app.before_first_request
def setup_logging():
    """Enable info-level logging."""
    if not app.debug:
        #app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


# Blueprints
import api
app.register_blueprint(api.app, url_prefix='/api')

# Import modules using dnstwister.app/cache/db/emailer here
import repository
import tools
import views.syndication.atom
import views.www.help
import views.www.index
import views.www.search
import views.www.status
import views.www.email
