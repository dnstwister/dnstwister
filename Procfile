web: waitress-serve --send-bytes=512 --port=$PORT dnstwister:app
worker_deltas: python -m dnstwister.workers.deltas
worker_email: python -m dnstwister.workers.email
worker_stats_windows: python -m dnstwister.workers.stats.update_windows
worker_stats_deltas: python -m dnstwister.workers.stats.update_deltas
