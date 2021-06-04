from .voc_const import *
import json
import requests
from tqdm import tqdm
import time

class VocdoniApi:
    def __init__(self, url):
        self.url = url

    def getProcessList(self, _from=None):
        r = self._api_call(
            _method=METHODS.getProcessList,
            _from=_from
        )
        
        return (r.get("response", r)
        .get("processList",  r))

    def getProcessInfo(self, processId):
        _r = self._api_call(
            _method=METHODS.getProcessInfo,
            processId=processId
        )
        
        r = _r.get("response", _r).get("process", _r)
        if isinstance(r, dict):
            # Keep only needed attributes
            # If r is an error it won't be a dict
            r = { attr: r[attr] for attr in ATTR.getProcessInfo 
            if attr in r}

        return r


    

    
    def getEnvelopeList(self, processId, max_env):
        output = []
        range_from_env = range(0, max_env, 64)

        for f in tqdm(range_from_env):
            r = self._getEnvelopeList(processId=processId, _from=f)
            time.sleep(.1)
            output.append(r)
            if len(r) != 64:
                # Got all envelopes from process
                break
        return output
    
    def getEnvelope(self, nullifier):
        _r = self._api_call(
            _method=METHODS.getEnvelope,
            nullifier=nullifier
        )

        r = _r.get("response", _r).get("envelope", _r).get("weight", _r)
        if isinstance(r, dict): r.update({"nullifier":nullifier})

        return r
    
    def _getEnvelopeList(self, processId, _from):
        _r = self._api_call(
            _method=METHODS.getEnvelopeList,
            processId=processId,
            _from=_from
        )
        
        r = _r.get("response", _r).get("envelopes", _r)
        output = []
        if isinstance(r, list):
            # Keep only needed attributes
            # If r is an error it won't be a list
            for env in r:    
                output.append({attr: env[attr] for attr in ATTR.getEnvelopeList 
                if attr in env})

        if output: 
            return output
        else:
            return r
    
    def _api_call(self, _method, _id=None, 
    _from=None, 
    processId=None,
    nullifier=None):
        _id = "123" if not _id else _id
        data = {
            "request": {
                "method": _method,
            },
            "id": _id,
        }

        if _from != None: data["request"]["from"] = _from
        if processId != None: data["request"]["processId"] = processId
        if nullifier != None: data["request"]["nullifier"] = nullifier
        try:
            r = requests.post(
                self.url, 
                data=json.dumps(data)
                )
            return json.loads(r.content)

        except Exception as e:
            return e

      