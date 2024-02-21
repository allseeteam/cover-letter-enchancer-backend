import json
import yaml


def read_yaml(path: str) -> dict:
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def read_json(path: str) -> dict:
    with open(path, 'r') as stream:
        return json.load(stream)