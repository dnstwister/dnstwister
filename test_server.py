"""Launch."""
from dnstwister import app

# At least until https://github.com/pallets/flask/pull/1910 is merged...
app.jinja_env.auto_reload = True

app.run(debug=True)
