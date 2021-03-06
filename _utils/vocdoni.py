from .voc_const import *
import json
import requests
from tqdm import tqdm
import time
from random import randint

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


    

    
    def getEnvelopeList(self, processId):
        output = []
        range_from_env = range(0, 2000000, 64)
        for f in tqdm(range_from_env):
            r = self._getEnvelopeList(processId=processId, _from=f)
            output.append(r)
            if not isinstance(r, list) or  len(r) != 64:
                # Got all envelopes from process or received error
                break
        return r
    
    def getEnvelope(self, nullifier):
        _r = self._api_call(
            _method=METHODS.getEnvelope,
            nullifier=nullifier
        )

        if isinstance(_r, dict):
            r = _r.get("response", _r).get("envelope", _r).get("weight", _r)
            return {"nullifier" : nullifier, "weight" : r}
        else:
            return _r
    
    def _getEnvelopeList(self, processId, _from):
        _r = self._api_call(
            _method=METHODS.getEnvelopeList,
            processId=processId,
            _from=_from
            )

        return _r
        
    
    def _api_call(self, _method, _id=None, 
    _from=None, 
    processId=None,
    nullifier=None,
    listSize=None):
        time.sleep(SLEEP_SECS+randint(10,100)/1000)
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
        if listSize != None: data["request"]["l istSize"] = listSize
        try:
            r = requests.post(
                self.url, 
                data=json.dumps(data)
                )
            return json.loads(r.content)

        except Exception as e:
            return str(e)

      