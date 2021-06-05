# Intro

# Requirements
- conda
- mongoDB

# Steps
1. Set Environment
  - Install conda env: `....`
  - Install python libraries: `...`

2. Execute: `pyton main.py`

# Note
Vocdoni API method `getEnvelopeList` takes a long time to respond (avg. 25s per call).
Threasds have been tested but it resulted into getting many timeouts.
For this reason, the most complete set of responses I was able to get was **cached**.
It took aprox 4 hours. 

In `_const.py` there is a constant `CACHE_ENVELOPES` set to `True` by default.
For executing this method just turn it to `False`.



