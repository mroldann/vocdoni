# Intro
In this repo you will be able to download Vochain data with `main.py` file.
Data will be stored in MongoDB collections for further analysis.


# Requirements
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- [mongoDB](https://docs.mongodb.com/manual/administration/install-community/)
- *The default port for mongo is `27017` so make sure it is available.*

# Steps
1) Clone repo
2) Change dir to repo dir
3) Set Environment
  - Install conda env using CLI: ```conda env create -n vocdoni-env --file environment.yml```
  - Activate env using CLI: ```conda activate vocdoni-env```
4) Execute using CLI: ```pyton main.py```

### Note
Vocdoni API methods `getEnvelopeList` and `getEnvelop` take a long time to respond (aprox. 5 hours each in sequence).
Threads and different `listSize` have been tested but it resulted into getting many timeouts or no speed win.
For this reason, the most complete set of responses I was able to get was **cached** in `/data`.

In `_const.py` there are two constants  set to `True` by default `CACHE_ENVELOPES` and `CACHE_WEIGHTS`.
Force to execute this methods by turning them to `False`.

## Analysis
Two HTML files are provided. Both contain the same findigs but one doesn't contain code instructions:
- `analysis.html`
- `analysis (with code).html`

*In order to watch graphs, iframe_figures/ dir is needed in the root path.*



