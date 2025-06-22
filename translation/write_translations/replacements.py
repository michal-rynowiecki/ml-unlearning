import gender_guesser.detector

from NER_recognition.find_entities import get_people, get_locations, random_name, get_gender, random_city

import random
import os

import pandas as pd
import numpy as np

'''
Adds an assigned name to an existing name in the dataset to replace it.

$ matchings:            dictionary of created matchings thus far
$ name:                 name to add to matchings
$ replacement_names:    
'''
def add_matching(matchings: dict, name: str, replacement_name: str, gendered: bool = False) -> dict:
    matchings[name] = replacement_name
    return matchings

'''
Function to build a lis of perturbed answers with the same properties as in the
original dataset
'''
def build_perturbed_line(list_of_answers_to_perturb, used_persons, used_locs, source, d, nlp):
    # This is the list of sentences with replaced people to return
    perturbed_lines = []

    perturbed_parent_folder = '../' + source + 'people/perturbed/'
    #print('SOURCE', perturbed_parent_folder)

    # Choose the folder with either the famous names or one of the random etnicity names
    choosen_pert_source = random.choice(os.listdir(perturbed_parent_folder))

    # Create the path for the folder
    perturbed_source_folder = perturbed_parent_folder + choosen_pert_source


    # FIRST CASE: FAMOUS
    if choosen_pert_source == 'f':
        df = pd.read_excel(perturbed_source_folder + '/famous.xlsx')

        # Get a different random name for every sentence in the perturbed answers list
        list_of_names = list(np.random.choice(a=df["name"], size=len(list_of_answers_to_perturb), replace=False))

        for sentence in list_of_answers_to_perturb:

            new_sentence = swap_persons_perturbed(sentence, used_persons, list_of_names.pop(0), nlp, source)
            locs_changed    = swap_locs(new_sentence, used_locs, source, nlp)

            perturbed_lines.append(locs_changed)
        
    # SECOND CASE: REGULAR
    else:
        for sentence in list_of_answers_to_perturb:
            people_changed  = swap_persons_perturbed_reg(sentence, used_persons, perturbed_source_folder, d, nlp)
            locs_changed    = swap_locs(people_changed, used_locs, source, nlp)
            
            perturbed_lines.append(locs_changed)

    return perturbed_lines

'''
Swap names if perturbation is to regular peopel of a different ethnicity
'''
def swap_persons_perturbed_reg(entry, used_persons, source, gender_detector, model):

    persons = get_people(entry, model)
    new_line = entry
    offset = 0

    # Go through each detect person
    for person in persons:
        # If they do not exist already in the used persons dictionary, create a new binding
        if person['name'] not in used_persons:
            gender = get_gender(person['name'].split()[0], gender_detector)

            # If the names are chinese, then the last name comes first, aka reverse order
            rev = True if 'chinese' in os.listdir(source) else False
            swap_name = get_foreign_name(gender, source, rev)

            new_name: str = last_name_val_pert(person['name'], 'm', used_persons, source = ('data/da-entity-names/people/'))
            if new_name: new_name = swap_name + ' ' + new_name.split()[-1]

            # If no one with the same last name exists, just create a full new name,
            # THIS IS THE DEFAULT CASE
            if not new_name:
                new_name = swap_name

            add_matching(used_persons, person['name'], new_name)
        else:
            new_name = used_persons[person['name']]

        start_loc   = person['start_c'] - offset
        finish_loc  = person['end_c'] - offset
        # Create the new line by cutting out the old entity and adding in the new one
        new_line = new_line[:start_loc] + used_persons[person['name']] + new_line[finish_loc:]

        offset = offset + len(person['name']) - len(new_name)

    return new_line


'''
Swap names if perturbation is to famous people
'''
def swap_persons_perturbed(entry, used_persons, swap_name, model, source):
    persons = get_people(entry, model)
    new_line = entry
    offset = 0

    for person in persons:
        # THE NORP should be a seperate category and possibly have a seperate function?
        if person['type'] == "NORP":
            add_matching(used_persons, person['name'], 'Danish')
            new_name = 'Danish'

        elif person['name'] not in used_persons:
            # Check for the last name
            new_name: str = last_name_val_pert(person['name'], 'm', used_persons, source = (source + 'people/'))
            if new_name: new_name = swap_name + ' ' + new_name.split()[-1]

            # If no one with the same last name exists, just create a full new name,
            # THIS IS THE DEFAULT CASE
            if not new_name:
                new_name = swap_name

            add_matching(used_persons, person['name'], new_name)
        else:
            new_name = used_persons[person['name']]

        start_loc   = person['start_c'] - offset
        finish_loc  = person['end_c'] - offset
        # Create the new line by cutting out the old entity and adding in the new one
        new_line = new_line[:start_loc] + used_persons[person['name']] + new_line[finish_loc:]

        offset = offset + len(person['name']) - len(new_name)

    return new_line



# TODO
# This is a doubled function from replace.py and needs fixing the import
def last_name_val_pert(name: str, gender, used_persons: dict, source:str):
    last_name = name.split()[-1]
    for existing_name in used_persons.keys():
        if last_name in existing_name:
            replacement_last_name = used_persons[existing_name].split()[-1]
            new_name = random_name(source, gender, last_name=False) + ' ' + replacement_last_name
            return new_name
    return False

# TODO
# This is a doubled function from replace.py and needs fixing the import
def swap_locs(entry, used_locs, source, model):
    locations = get_locations(entry, model)
    new_line = entry
    offset = 0

    # Get replacements for locations
    for location in locations:
        if location['type'] == 'country':
            used_locs[location['name']] = 'Denmark'
        elif location['name'] not in used_locs and location['type'] == 'city':
            add_matching(used_locs, location['name'], random_city(source))
        
        if location['type'] == 'country' or location['type'] == 'city':
            start_loc   = location['start_c'] - offset
            finish_loc  = location['end_c'] - offset

            offset = len(location['name']) - len(used_locs[location['name']])
            # Create the new line by cutting out the old entity and adding in the new one
            new_line = new_line[:start_loc] + used_locs[location['name']] + new_line[finish_loc:]
        else:
            1
            #TODO figure out what to do with non city and non country locations
    return new_line


def get_foreign_name(gender, source, reverse=False):
    gen = 'men' if gender == 'm' else 'women'
    df = pd.read_excel(source + '/' + gen + '.xlsx')
    last = pd.read_excel(source + '/' + 'last.xlsx')
    
    name1, name2 = np.random.choice(a=df["name"], size=2, replace=False)[0:2]
    last_name = np.random.choice(a=last["name"], size=1, replace=False)[0]

    if reverse:
        swap_name = f"{last_name} {name1} {name2}"
    else:
        swap_name = f"{name1} {name2} {last_name}"

    return swap_name