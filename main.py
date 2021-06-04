if __name__ ==  '__main__':
    from _const import *
    from _utils import vocdoni
    from _utils._mongo import (vocdoni_db,  
    col_processes, col_envelopes)
    from concurrent.futures import ProcessPoolExecutor
    import json
    from tqdm import tqdm
    import pandas as pd

    voc_api = vocdoni.VocdoniApi(URL)
    range_from = range(
        0, 
        MAX_PROCESSES,
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
    print(df_processes.head())
    print(df_processes.columns)

    print("Getting data from envelopes") # 25.79s/it before Pool
    with ProcessPoolExecutor(max_workers=MAX_POOL_WORKERS) as executor:
        future_results = {executor.submit(voc_api.getEnvelopeList,
        p, MAX_ENVELOPES): p for p in processes[:1]}
        
    
    envelopes_dict_list = [z for x in future_results 
    for y in x.result()
    for z in y
    ] # nested list
    print(envelopes_dict_list)
    print(len(envelopes_dict_list))
    
    nullifiers = [x.get('nullifier') for x in envelopes_dict_list
    if 'nullifier' in x]

    print(nullifiers)

    with ProcessPoolExecutor(max_workers=MAX_POOL_WORKERS) as executor:
        future_results = {executor.submit(voc_api.getEnvelope,
        n): n for n in nullifiers[:20]}

    nullifiers_result = [x.result() for x in future_results]

    print(nullifiers_result)
    
