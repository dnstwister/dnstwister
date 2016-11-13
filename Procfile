web: waitress-serve --send-bytes=512 --port=$PORT dnstwister:app
worker_deltas: python -m dnstwister.worker_deltas
worker_email: python -m dnstwister.worker_email
