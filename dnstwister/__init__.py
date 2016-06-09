"""dnstwister web app."""
import flask
import flask.ext.cache

import mail.sendgridservice
import payment.stripeservice
import storage.pg_database


# Set up app/cache/db/emailer/gateway here
app = flask.Flask(__name__)
cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})
db = storage.pg_database.PGDatabase()
emailer = mail.sendgridservice.SGSender()
gateway = payment.stripeservice.StripeService()

# Blueprints
import apis
app.register_blueprint(apis.app, url_prefix='/api')

import apis.analysis
app.register_blueprint(apis.analysis.app, url_prefix='/api/analysis')


# Import modules using dnstwister.app/cache/db/emailer here
import repository
import tools
import views.syndication.atom
import views.www.help
import views.www.index
import views.www.search
import views.www.status
import views.www.whois
import views.www.email
