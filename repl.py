import json

import lib.pysquared.pysquared as pysquared

with open("config.json", "r") as f:
    json_data = f.read()
config = json.loads(json_data)

print("Initializing a cubesat object as `c` in the REPL...")
c = pysquared.Satellite()
