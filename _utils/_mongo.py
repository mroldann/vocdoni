import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
vocdoni_db= myclient["vocdoni_db"]

col_processes = vocdoni_db["processes"]
col_envelopes = vocdoni_db["envelopes"]

# Drop if exists
def drop_collections():
    col_processes.drop()
    col_envelopes.drop()