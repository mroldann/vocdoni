if __name__ ==  '__main__':
    from _const import *
    from _utils import vocdoni
    from _utils.voc_const import *
    from _utils._mongo import (vocdoni_db,  
    col_processes, col_envelopes, drop_collections)
    from concurrent.futures import ProcessPoolExecutor
    import json
    from tqdm import tqdm
    import pandas as pd

    drop_collections()

    print("\n\n\n### Starting VocdoniApi processing ###")
    voc_api = vocdoni.VocdoniApi(URL)
    range_from = range(
        0, 
        MAX_PROCESSES,
        64
    )
    processes = []
    errs = []
    print("\nGetting processes list:")
    for f in tqdm(range_from):
        r = voc_api.getProcessList(_from=f)
        if isinstance(r, list):
            processes.extend(r)
        else:
            errs.extend((f, r))
    
    print("- Total processes found:", len(processes))

    processes_dict_list = []
    print("\nGetting processes data:")
    for p in tqdm(processes):
        r = voc_api.getProcessInfo(processId=p)
        processes_dict_list.append(r)

    print("\nInserting into processes collection")
    col_processes.insert_many(processes_dict_list)
    
    print("\nGetting data from envelopes") # 25.79s/it before Pool
    
    envelopes_dict_list = []
    if CACHE_ENVELOPES:
        print("\n- Cache imported.")
        from data.rs import rs as envelopes_dict_list
    else:
        print("\n- API call: getEnvelopeList")
        for p in tqdm(processes):
            envelopes_dict_list.append(voc_api.getEnvelopeList(p, MAX_ENVELOPES))

    
    print("\nenvelopes_dict_list")
    print("- Total envelopes: ", len(envelopes_dict_list))
    
    envelopes_filtered = []
    for e in envelopes_dict_list:
        r = e.get("response", None)
        _e = r.get("envelopes", None)
        if _e:
            l = (len(_e))
            for _d in _e:
                new = {attr: _d[attr] for attr in ATTR.getEnvelopeList if attr in _d}
                envelopes_filtered.append(new)
    
   
    nullifiers = []

    print("envelopes_filtered: ", len(envelopes_filtered))
    print(envelopes_filtered[:3])
    
    print("\nInserting into envelopes collection")
    col_envelopes.insert_many(envelopes_filtered)


    for env in envelopes_filtered:
        nullifiers.append(env.get('nullifier', None))

    print("\nnullifiers")
    print(nullifiers[:10])
    print(len(nullifiers))
    with open('nullifiers.txt', 'w') as f:
        for item in nullifiers:
            f.write("%s\n" % item)

    nullifiers_result = []
    
    with open('nullifiers_result.txt', 'w') as f:        
        for n in tqdm(nullifiers[:10]):
            r = voc_api.getEnvelope(n)
            nullifiers_result.append(r)
            f.write("%s\n" % r)

    print("\nnullifiers_result")
    print(nullifiers_result[:10])
    print(len(nullifiers_result))
    

    