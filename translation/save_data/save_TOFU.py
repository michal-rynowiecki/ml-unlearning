import json

def dict_to_line(dic: dict) -> dict:
    line = json.dumps(dic)
    return line

def write_tofu(line: str, path: str) -> None:
    with open('../'+path, 'a') as f:
        f.write(line)
