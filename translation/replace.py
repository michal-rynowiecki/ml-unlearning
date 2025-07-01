# TODO make a function that reduces the doubling in the code. 

'''
GUIDE

Use the function replace and save with appropriate arguments to
replace the entities from the source to the output
'''

LINES_PER_AUTHOR            = 20
NER_MODEL                   = "en_core_web_trf"

from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from NER_recognition.find_entities import get_people, get_locations, get_awards, random_name, get_gender, random_city, random_award
from write_translations.replacements import add_matching, build_perturbed_line

import gender_guesser.detector as gender

import os
import random

import spacy

def replace_and_save(used_awards, used_persons, used_locs, source_file, output_file, replacements_path):
    nlp = spacy.load(NER_MODEL) # Change the NER model here

    source = replacements_path
    # names that have already been assigned and cannot be used again
    
    
    d = gender.Detector()

    source_path = obtain_file_path(source_file)

    with open(source_path, 'r') as f:
        # Counter to reset the name dictionary
        reset           = LINES_PER_AUTHOR
        current_author  = None

        while True:
            # This dictionary will serve as the new line in the new file with entities replaced
            build_replaced_line = {}

            # read a line from the source file
            try:
                line = line_to_dict(f.readline())
            except:
                return

            # If we went through all the lines about a particular author, reset the counter
            if reset == 0:
                reset = LINES_PER_AUTHOR
                current_author = None

            
            # For every value in the dictionary from the json file single line iterate through
            # its text value and replace their contents
            for key in line:

                # If we didnt assign the author described in the next #LINES_PER_AUTHOR lines,
                # attempt to do that
                if not current_author:
                    try:
                        current_author = get_people(line[key], nlp)[0]['name']
                    except:
                        1

                print("current author: ", current_author)
                p = random.random()
                if key == 'perturbed_answer' and p <= 0.33:
                    # Get a value that will determine if non-Danish entities should be the ones
                    # in the perturbed list, in this case the threshold is 0.33 for non-danish names
                        build_replaced_line[key] = build_perturbed_line(line[key], used_persons, used_locs, source, d, nlp)
                # If the key is a list, go through each element and append them to the list
                elif type(line[key]) == list:
                    build_replaced_line[key] = []
                    for answer in line[key]:
                        people_changed  = swap_persons(answer, used_persons, source, d, nlp, current_author)
                        locs_changed    = swap_locs(people_changed, used_locs, source, nlp)
                        # awards_changed  = swap_awards(locs_changed, used_awards, source, nlp)

                        build_replaced_line[key].append(locs_changed)
                # Else it has just a single value
                else:
                    people_changed  = swap_persons(line[key], used_persons, source, d, nlp, current_author)
                    locs_changed    = swap_locs(people_changed, used_locs, source, nlp)
                    # awards_changed  = swap_awards(locs_changed, used_awards, source, nlp)

                    
                    build_replaced_line[key] = locs_changed
                    #build_replaced_line[key] = awards_changed
                

            line_to_write = dict_to_line(build_replaced_line) + '\n'

            write_tofu(line_to_write, output_file)

            # Count to LINES_PER_AUTHOR
            reset -= 1

'''
Get a line and replace the locations in it

$ entry:        line of text for which entities will be swapped
$ used_locs:    dictionary of locations which were already replaced and their replacements
$ source:       path with a list of cities
'''
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
        # In case a city and country were recognized as a single entity,
        # replace it with a city and add Denmark after it
        elif location['type'] == 'GEP' or location['type'] == 'GPE':
            add_matching(used_locs, location['name'], random_city(source))
            used_locs[location['name']] += ', Denmark'
        
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

'''
Swap persons in a sentence

$ entry             - line of text for which the entities will be swapped
$ used_persons      - dictionary of people already replaced and their replacements 
$ source            - path with files containing names and their probabilities
$ gender_detector   - gender detector object used for predicting the gender of a person
$ model             - SpaCy model used for NER
'''
def swap_persons(entry, used_persons, source, gender_detector, model, current_author):
    source = source + 'people/'
    persons = get_people(entry, model)
    new_line = entry
    offset = 0

    for person in persons:

        # THE NORP should be a seperate category and possibly have a seperate function?
        # Should it even be used?
        if person['type'] == "NORP":
            # add_matching(used_persons, person['name'], 'Danish')
            add_matching(used_persons, person['nationality'], 'Danish')
            new_name = 'Danish'

        elif person['name'] not in used_persons:
            gender = get_gender(person['name'].split()[0], gender_detector)

            # If the name is not in used persons dict, look if only the first name has been used
            new_name: str = first_name_val(current_author, person['name'], gender, used_persons, source)

            # If the full name is not in the used persons dict, check for the last name
            if not new_name:
                new_name: str = last_name_val(person['name'], gender, used_persons, source)

            # If no one with the same last name exists, just create a full new name,
            # THIS IS THE DEFAULT CASE
            if not new_name:
                new_name = random_name(source, gender)

            

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
Detect and replace awards in the provided text line
'''
def swap_awards(entry, used_awards, source, model):
    new_line = entry
    offset = 0
    awards = get_awards(entry, model)

    for award in awards:
        if award not in list(used_awards.keys()):
            add_matching(used_awards, award['name'], random_award(source))

        start_loc   = award['start_c'] - offset
        finish_loc  = award['end_c'] - offset
        offset = len(award['name']) - len(used_awards[award['name']])
        
        # Create the new line by cutting out the old entity and adding in the new one
        new_line = new_line[:start_loc] + used_awards[award['name']] + new_line[finish_loc:]    
    
    return new_line



'''
Check if the person to be replaced shares a last name
with anyone in the already replaced people. If yes,
return the previously replaced person's last name.
This is created for the perturbed data set or in the case
that there are family members.
$ name -            name that is getting replaced
$ used_persons -    dictionary of replacements
'''
def last_name_val(name: str, gender, used_persons: dict, source:str):
    last_name = name.split()[-1]
    for existing_name in used_persons.keys():
        if last_name in existing_name:
            replacement_last_name = used_persons[existing_name].split()[-1]
            new_name = random_name(source, gender, last_name=False) + ' ' + replacement_last_name
            return new_name
    return False

# For all exising names in the dictionary, check if the current looked for name is part of a full name already
# in the dictionary
def first_name_val(current_name, looked_name, gender, used_persons, source):
    # If the current first name of the author is the same as the first name of who we are looking for, return
    # the first name of the replacing name for the current author
    current_first = current_name.split()[0]
    if (current_name in used_persons.keys()) and looked_name.split()[0] == current_first:
        return used_persons[current_name].split()[0]

    # For every first name in the dictionary
    for name in used_persons.keys():
        first = name.split()[0]

        if first == looked_name.split()[0]:
            return used_persons[name].split()[0]
    return False



def replace_directory(input, output, data):
    used_persons    = {}
    used_locs       = {}
    used_awards     = {} 
    
    files = [item for item in os.listdir('../' + input) if not item[0] == '.' and not item == 'README.md']
    
    for file in files:
        replace_and_save(used_awards, used_persons, used_locs, input + '/' + file, output + '/r' + file, data)

#replace_directory('TOFU', 'rTOFU', 'data/da-entity-names/')

replace_and_save({}, {}, {}, 'TOFU/forget01_perturbed.json', 'rTOFU/rforget01_perturbed.json', 'data/da-entity-names/')