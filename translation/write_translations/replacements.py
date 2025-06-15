import random
import gender_guesser.detector

'''
Adds an assigned name to an existing name in the dataset to replace it.

$ matchings:            dictionary of created matchings thus far
$ name:                 name to add to matchings
$ replacement_names:    
'''
def add_matching(matchings: dict, name: str, replacement_names: str, gendered: bool = False) -> dict:
    with open('../' + replacement_names, 'r') as f:
        # TODO - GENDER MATCHING
        # if gendered: gender guesser
        #   if male, get male replacement path
        #   if female, get female replacement path
        #   if unkown, get either


        # TODO change length of random to be the number of names, requires more names
        n = random.randrange(0, 50)
        for i in range(n):
            f.readline()
        replacement_name = f.readline().strip()

    matchings[name] = replacement_name
    return matchings