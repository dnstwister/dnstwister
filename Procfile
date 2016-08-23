web: waitress-serve --send-bytes=512 --port=$PORT dnstwister:app
worker_deltas: python dnstwister/worker_deltas.py
worker_email: python dnstwister/worker_email.py
