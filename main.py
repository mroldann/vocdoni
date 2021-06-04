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

    print('MAX_POOL_WORKERS', MAX_POOL_WORKERS)
    print('N', N)

    processes = []
    errs = []
    print("\nGetting processes list:")
    for f in tqdm(range_from):
        print(f)
        r = voc_api.getProcessList(_from=f)
        if isinstance(r, list):
            processes.extend(r)
        else:
            errs.extend((f, r))
    
    print(len(processes))

    processes_dict_list = []
    print("\nGetting processes data")
    for p in tqdm(processes):
        r = voc_api.getProcessInfo(processId=p)
        processes_dict_list.append(r)

    print("\nInserting into processes collection")
    col_processes.insert_many(processes_dict_list)
    
    with open('processess.txt', 'w') as f:
        for item in processes_dict_list:
            f.write("%s\n" % item)


    myresult = col_processes.find()
    myresult = [x for x in myresult]
    df_processes = pd.DataFrame(myresult)
    print(df_processes.head())
    print(df_processes.columns)

    print("\nGetting data from envelopes") # 25.79s/it before Pool
    with ProcessPoolExecutor(max_workers=MAX_POOL_WORKERS) as executor:
        future_results = {executor.submit(voc_api.getEnvelopeList,
        p, MAX_ENVELOPES): p for p in processes[:N]}
        
    envelopes_dict_list = [y for x in future_results 
    for y in x.result()
    ] # nested list
            
    with open('envelopes.txt', 'w') as f:
        for item in envelopes_dict_list:
            f.write("%s\n" % item)

    print("\nenvelopes_dict_list")
    print(envelopes_dict_list)
    print(len(envelopes_dict_list))
    
    nullifiers = []
    for env_list in envelopes_dict_list:
        if isinstance(env_list, list):
            for env in env_list:
                nullifiers.append(env.get('nullifier', None))

    print("\nnullifiers")
    print(nullifiers)
    print(len(nullifiers))

    with ProcessPoolExecutor(max_workers=MAX_POOL_WORKERS) as executor:
        future_results = {executor.submit(voc_api.getEnvelope,
        n): n for n in nullifiers}

    nullifiers_result = [x.result() for x in future_results]

    print("\nnullifiers_result")
    print(nullifiers_result)
    print(len(nullifiers_result))
    

