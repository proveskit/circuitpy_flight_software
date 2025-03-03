import json

import storage

with open("config.json", "r") as f:
    json_data = f.read()
parameters = json.loads(json_data)
if parameters["read_state"]:
    print("read_state=true")
    storage.enable_usb_drive()
else:
    print("read_state=false")
    storage.disable_usb_drive()

# import supervisor
# supervisor.set_next_stack_limit(4096 + 4096)
