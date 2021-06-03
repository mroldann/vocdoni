from pathlib import Path


URL = 'https://gw1.dev.vocdoni.net/dvote'
MAX_PROCESSES = 200

class PATHS:
    DATA = Path('data')


PATHS.DATA.mkdir(exist_ok=True)