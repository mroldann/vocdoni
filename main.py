if __name__ ==  '__main__':
    from _const import *
    from _utils import vocdoni
    from _utils.voc_const import *
    from _utils._mongo import (col_processes, col_envelopes, drop_collections, get_collections, MONGO_HOST)
    from tqdm import tqdm
    import pandas as pd
    from datetime import timedelta

    drop_collections()

    print("\n\n\n### Starting VocdoniApi processing ###")
    print(f"MongoDB host: {MONGO_HOST}")
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
    for p in tqdm(processes[:N]):
        r = voc_api.getProcessInfo(processId=p)
        processes_dict_list.append(r)

    print("\nInserting into processes collection")
    col_processes.insert_many(processes_dict_list)
    
    myresult = col_processes.find()
    myresult = [x for x in myresult]
    df_processes = pd.DataFrame(myresult)
    MIN_KNOWN_DATE = pd.to_datetime(df_processes['creationTime']).min()
    
    print("\nGetting data from envelopes") # 25.79s/it before Pool
    
    envelopes_dict_list = []
    if CACHE_ENVELOPES:
        print("\n- Cache imported.")
        from data.rs import rs as envelopes_dict_list
    else:
        print("\n- API call: getEnvelopeList")
        for p in tqdm(processes[:N]):
            response = voc_api.getEnvelopeList(p)
            if isinstance(response, dict):
                envelopes_dict_list.append(response)

    
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
    for env in envelopes_filtered:
        nullifiers.append(env.get('nullifier', None))

    weights_response = []
    
    if CACHE_WEIGHTS:
        from data.weights import weights as _weights_response
        print("\n- Weights imported.")
        weights_response = []
        for r in _weights_response:
            if isinstance(r, dict):
                e = r.get("response").get("envelope")
                n = e.get("meta").get("nullifier")
                w = e.get("weight")
                weights_response.append({
                    "nullifier" :n,
                    "weight" : w
                })

    else:
        print("\n- API call: getEnvelope")
        for n in tqdm(nullifiers[:N]):
            r = voc_api.getEnvelope(n)
            weights_response.append(r)


    
    weights_dict = {}

    for w_r in weights_response:
        if isinstance(w_r, dict):
            nullifier = w_r.get("nullifier")
            weight = w_r.get("weight")
            if weight:
                weights_dict[nullifier] = weight


    print(f"\nAdding weight and timestamp to envelopes\nMIN_KNOWN_DATE: {MIN_KNOWN_DATE}")
    
    for env in envelopes_filtered:
        nullifier = env.get("nullifier")
        # Set to 0 if not found
        env["weight"] = weights_dict.get(nullifier, 0)
        days = (env["height"]/ AVG_BLOCK_TIME_SECS # seconds
                / 60 # minutes
                / 24 # days
                )
        env["vote_ts"] = timedelta(days=days) + MIN_KNOWN_DATE

    print("\nInserting into envelopes collection")
    col_envelopes.insert_many(envelopes_filtered)

    print("\n - Checking database collections: ", get_collections())

    print("\n - Checking collections head: ")
    print("\t - Processes: ")
    myresult = col_processes.find()
    myresult = [x for x in myresult]
    print(myresult[:5])
    print(f"\t - Total rows: {len(myresult)}")

    print("\n\t - Envelopes: ")
    myresult = col_envelopes.find()
    myresult = [x for x in myresult]
    print(myresult[:5])
    print(f"\t - Total rows: {len(myresult)}")
    

    print("\n\n\n### Finished VocdoniApi execution ###")