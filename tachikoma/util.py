import json
from datetime import datetime


class TachiKomaJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        try:
            return super().default(self, o)
        except Exception as e:
            print("Broken!")
            raise
