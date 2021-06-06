# Intro
In this repo you will be able to download Vochain data with `main.py` file.
Data will be stored in MongoDB collections for further analysis.


# Requirements
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- [mongoDB](https://docs.mongodb.com/manual/administration/install-community/)
- *The default port for mongo is `27017` so make sure it is available.*

# Steps
1. Set Environment
  - Install conda env: ```conda env create -n vocdoni-env --file environment.yml```
  - Activate env: ```conda activate vocdoni-env```
2. Execute: ```pyton main.py```

# Note
Vocdoni API method `getEnvelopeList` and `getEnvelop` take a long time to respond (aprox. 5 hours each in sequence).
Threads and different `listSize` have been tested but it resulted into getting many timeouts or no speed win.
For this reason, the most complete set of responses I was able to get was **cached** in `/data`.

In `_const.py` there are two constants  set to `True` by default `CACHE_ENVELOPES` and `CACHE_WEIGHTS`.
For executing this methods just turn it to `False`.



