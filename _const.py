from pathlib import Path

URL = 'https://gw1.dev.vocdoni.net/dvote'
# Source: https://explorer.dev.vocdoni.net/
MAX_PROCESSES = 200
MAX_ENVELOPES = 1600000
AVG_BLOCK_TIME_SECS = 10

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)

N = 2000000 # Used for debugging
CACHE_ENVELOPES = True
CACHE_WEIGHTS = True