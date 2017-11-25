web: waitress-serve --send-bytes=512 --port=$PORT dnstwister:app
worker_deltas: python -m dnstwister.workers.deltas
worker_email: python -m dnstwister.workers.email
worker_stats: python -m dnstwister.workers.stats
