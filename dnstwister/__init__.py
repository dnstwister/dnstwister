"""dnstwister web app."""
import flask
import flask.ext.cache

import storage.pg_database

# Set up app/cache/db here
app = flask.Flask(__name__)
db = storage.pg_database.PGDatabase()
cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})

# Import modules using dnstwister.app/cache/db here
import repository
import tools
import views.syndication.atom
import views.www.index
import views.www.search
import views.www.whois
import views.www.email
import views.api.ip
