import bson
import datetime
import json
from functools import partial


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "$date": obj.timestamp() * 1000
            }
        if isinstance(obj, bson.ObjectId):
            return str(obj)
        return super(DatetimeEncoder, self).default(obj)

def date_loads(obj):
    tdate = obj.get('$date')
    if tdate:
        return datetime.datetime.fromtimestamp(tdate / 1000)
    for key, val in obj.items():
        if val:
            try:
                obj[key] = bson.ObjectId(val)
            except Exception:
                pass
    return obj

json.dumps = partial(json.dumps, cls=DatetimeEncoder)
json.loads = partial(json.loads, object_hook=date_loads)
