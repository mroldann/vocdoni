import pymongo
import pandas as pd

MONGO_HOST = "mongodb://localhost:27017/"
myclient = pymongo.MongoClient(MONGO_HOST)
vocdoni_db= myclient["vocdoni_db"]

col_processes = vocdoni_db["processes"]
col_envelopes = vocdoni_db["envelopes"]

def drop_collections():
    # Drop if exists
    col_processes.drop()
    col_envelopes.drop()

def get_df_processes():
    processes = col_processes.find()
    processes = [x for x in processes]
    return pd.DataFrame(processes)

def get_df_envelopes():
    envelopes = col_envelopes.find()
    envelopes = [x for x in envelopes]
    return pd.DataFrame(envelopes)

def get_collections():
    return vocdoni_db.list_collection_names()
