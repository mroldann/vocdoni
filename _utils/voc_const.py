class METHODS:
        getInfo = "getInfo"
        getProcessList = "getProcessList"  
        getProcessInfo = "getProcessInfo"
        getEnvelopeList = "getEnvelopeList"
        getEnvelope = "getEnvelope"

class ATTR:
        getProcessInfo = ["creationTime", "endBlock", "startBlock", "entityId", "processId"]
        getEnvelopeList = ['height', 'nullifier', 'process_id']
        getEnvelope = ['weight']
        to_datetime = ["creationTime"]

SLEEP_SECS = .1
LIST_SIZE = 1