import random
import gender_guesser.detector

'''
Adds an assigned name to an existing name in the dataset to replace it.

$ matchings:            dictionary of created matchings thus far
$ name:                 name to add to matchings
$ replacement_names:    
'''
def add_matching(matchings: dict, name: str, replacement_name: str, gendered: bool = False) -> dict:
    matchings[name] = replacement_name
    return matchings