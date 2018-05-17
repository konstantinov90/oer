import json
import jsonschema

schema = {
    "$schema": "http://json-schema.org/draft-04/schema",
    'type': 'object',
    'properties': {
        'price': {'type': 'number'},
        'date': {'type': 'string', 'format': 'date-time'},
    },
}
import datetime
td = datetime.datetime.now()
o = {'price': 123.12, 'date': td}

jsonschema.validate(json.dumps(o), schema, format_checker=jsonschema.FormatChecker())
