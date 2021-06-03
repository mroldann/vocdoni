from .voc_const import *
import json
import requests


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

    def getEnvelopeList(self, processId, _from):
        _r = self._api_call(
            _method=METHODS.getEnvelopeList,
            processId=processId,
            _from=_from
        )
        
        r = _r.get("response", _r).get("envelopes", _r)
        if isinstance(r, dict):
            # Keep only needed attributes
            # If r is an error it won't be a dict
            r = { attr: r[attr] for attr in ATTR.getEnvelopeList 
            if attr in r}

        return _r
    
    def _api_call(self, _method, _id=None, _from=None, processId=None):
        _id = "123" if not _id else _id
        data = {
            "request": {
                "method": _method,
            },
            "id": _id,
        }

        if _from != None: data["request"]["from"] = _from
        if processId != None: data["request"]["processId"] = processId
        try:
            r = requests.post(
                self.url, 
                data=json.dumps(data)
                )
            return json.loads(r.content)

        except Exception as e:
            return e

      