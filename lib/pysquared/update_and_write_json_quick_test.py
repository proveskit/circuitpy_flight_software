import json


def write_to_config(key, value):
    new_pair = {key: value}
    with open("config.json", "r") as f:
        json_data = json.loads(f.read())

    json_data.update(new_pair)

    with open("config.json", "w") as f:
        f.write(json.dumps(json_data))


def update_config(key, value):
    with open("config.json", "r") as f:
        json_data = json.loads(f.read())

    json_data[key] = value

    with open("config.json", "w") as f:
        f.write(json.dumps(json_data))
