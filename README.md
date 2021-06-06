# Intro

# Requirements
- conda
- mongoDB
  - The default port for mongo is `27017`

# Steps
1. Set Environment
  - Install conda env: ```conda env create -n vocdoni-env --file environment.yml```
  - Activate env: ```conda activate vocdoni-env```
2. Execute: ```pyton main.py```

# Note
Vocdoni API method `getEnvelopeList` and `getEnvelop` take a long time to respond (aprox. 5 hours each in sequence).
Threasds and different `listSize` have been tested but it resulted into getting many timeouts or no speed win.
For this reason, the most complete set of responses I was able to get was **cached**.

In `_const.py` there are two constants  set to `True` by default `CACHE_ENVELOPES` and `CACHE_WEIGHTS`.
For executing this method just turn it to `False`.



