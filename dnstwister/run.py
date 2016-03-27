"""Launch."""
import sys

from dnstwister import app
app.run(debug=(sys.argv[-1] == '-d'))
