from _const import *
from _utils import vocdoni
from _utils._mongo import (vocdoni_db,  
col_processes, col_envelopes)
import json
from tqdm import tqdm
import pandas as pd

print(vocdoni_db.list_collection_names())


voc_api = vocdoni.VocdoniApi(URL)

range_from = range(
    0, 
    MAX_PROCESSES,
    64
)

range_from_env = range(
    0, 
    MAX_ENVELOPES,
    64
)

processes = []
errs = []
print("Getting processes list:")
for f in tqdm(range_from):
    print(f)
    r = voc_api.getProcessList(_from=f)
    if isinstance(r, list):
        processes.extend(r)
    else:
        errs.extend((f, r))



processes_dict_list = []
print("Getting data from processes")
for p in tqdm(processes[:20]):
    r = voc_api.getProcessInfo(processId=p)
    processes_dict_list.append(r)

print("Inserting into processes collection")
col_processes.insert_many(processes_dict_list)


myresult = col_processes.find()
myresult = [x for x in myresult]
df_processes = pd.DataFrame(myresult)
# df_processes['blocks'] = df_processes['endBlock'] - df_processes['startBlock']
# print(df_processes['blocks'].describe())
print(df_processes.head())
print(df_processes.columns)

envelopes_dict_list = []
print("Getting data from envelopes") # 25.79s/it
for p in tqdm(processes[:20]):
        r = voc_api.getEnvelopeList(processId=p, max_env=MAX_ENVELOPES)
        envelopes_dict_list.append(r)
        # TODO: thread pool!
    

print(envelopes_dict_list)
print(len(envelopes_dict_list))