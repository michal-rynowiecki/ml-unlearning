import os
from pathlib import Path
from io import StringIO
import json

'''
Return a file path relative to the base repo location (ml-unlearning)
'''
def obtain_file_path(path:str) -> str:
    # Make the path be relative to the whole repo  
    p = Path("../" + path)

    return p

'''
Takes a .json line from a file and returns a dictionary of that line
'''
def line_to_dict(line: str) -> dict:
    line_dictionary = json.loads(line)
    return line_dictionary
