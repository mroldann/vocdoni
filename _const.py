from pathlib import Path

URL = 'https://gw1.dev.vocdoni.net/dvote'
# Source: https://explorer.dev.vocdoni.net/
MAX_PROCESSES = 200
MAX_ENVELOPES = 1600000
AVG_BLOCK_TIME_SECS = 10


MAX_POOL_WORKERS = 3
N = 20

# OK: (3, 10), (3, 20) 
# KO: (5, 10), (4, 10)