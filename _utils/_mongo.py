import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
vocdoni_db= myclient["vocdoni_db"]

# Drop if exists
col_processes = vocdoni_db["processes"]
col_envelopes = vocdoni_db["envelopes"]

col_processes.drop()
col_envelopes.drop()