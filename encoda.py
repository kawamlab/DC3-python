import json
from dataclasses import dataclass
from data import log_output
 
def expireEncoda(object):
    if isinstance(object, log_output()):
        return object.isoformat()
 
dict = {"data": log_output()}
 
enc = json.dumps(dict, default=expireEncoda)
 
print(enc)
