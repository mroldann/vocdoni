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
    from datetime import timedelta

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
    
    envelopes_filtered = []
    for e in envelopes_dict_list:
        r = e.get("response", None)
        _e = r.get("envelopes", None)
        if _e:
            l = (len(_e))
            for _d in _e:
                new = {attr: _d[attr] for attr in ATTR.getEnvelopeList if attr in _d}
                envelopes_filtered.append(new)
    
    print(envelopes_filtered[:3])
    
    nullifiers = []
    for env in envelopes_filtered:
        nullifiers.append(env.get('nullifier', None))

    weights_response = []
    
    if CACHE_WEIGHTS:
        from data.weights import weights as weights_response
        print("\n- Weights imported.")
    else:
        print("\n- API call: getEnvelope")
        for n in tqdm(nullifiers[:10]):
            r = voc_api.getEnvelope(n)
            weights_response.append(r)

    print("\nweights_response")
    print(weights_response[:10])
    print(len(weights_response))
    
    weights_dict = {}

    for w_r in weights_response:
        if isinstance(w_r, dict):
            env = w_r.get("response", None).get("envelope", None)
            if env:
                nullifier = env.get("meta", None).get("nullifier", None)
                weight = env.get("weight", None)
                if weight:
                    weights_dict[nullifier] = weight

    print(weights_dict)

    print("\nAdding weight and timestamp to envelopes")
    for env in envelopes_filtered:
        nullifier = env.get("nullifier")
        # Set to 0 if not found
        env["weight"] = weights_dict.get(nullifier, 0)
        env["vote_ts"] = timedelta(day=(float(env["height"])/ AVG_BLOCK_TIME_SECS # seconds
                            / 60 # minutes
                            / 24 # days
                            ) + MIN_KNOWN_DATE

    print(envelopes_filtered[:10])
    print("\nInserting into envelopes collection")
    col_envelopes.insert_many(envelopes_filtered)