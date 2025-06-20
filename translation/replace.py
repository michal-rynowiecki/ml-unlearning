# TODO make a function that reduces the doubling in the code. 

'''
GUIDE

Use the function replace and save with appropriate arguments to
replace the entities from the source to the output
'''

from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from NER_recognition.find_entities import get_people, get_locations, random_name, get_gender, random_city
from write_translations.replacements import add_matching

import gender_guesser.detector as gender

import os

def replace_and_save(source_file, output_file, replacements_path):
    source = replacements_path
    # names that have already been assigned and cannot be used again
    used_persons = {}
    used_locs = {}
    d = gender.Detector()

    source_path = obtain_file_path(source_file)

    with open(source_path, 'r') as f:
        while True:
            # This dictionary will serve as the new line in the new file with entities replaced
            build_replaced_line = {}

            # read a line from the source file
            try:
                line = line_to_dict(f.readline())
            except:
                return
            
            # For every value in the dictionary from the json file single line iterate through
            # its text value and replace their contents
            for key in line:
                print('BEFORE: ', line[key])
                # If the key is a list, go through each element and append them to the list
                # TODO
                # If the perturbed list contains famous people, try to detect that and do not
                # change the famous person part of the name e.g. Marie Curie Al-Jazir should
                # be changed to e.g. Marie Curie Jensen
                if type(line[key]) == list:
                    build_replaced_line[key] = []
                    for answer in line[key]:
                        people_changed  = swap_persons(answer, used_persons, d)
                        locs_changed    = swap_locs(people_changed, used_locs, source)
                        build_replaced_line[key].append(locs_changed)
                # Else it has just a single value
                else:
                    people_changed  = swap_persons(line[key], used_persons, d)
                    locs_changed    = swap_locs(people_changed, used_locs, source)

                    print('AFTER: ', locs_changed)
                    build_replaced_line[key] = locs_changed
                print(build_replaced_line)

            line_to_write = dict_to_line(build_replaced_line) + '\n'
            #print('LINE TO WRITE: ', line_to_write)
            write_tofu(line_to_write, output_file)

# For each entry in the line dictionary
# $ entry: line of text for which entities will be swapped
# $ used_locs: dictionary of locations with which to replace
def swap_locs(entry, used_locs, source):
    locations = get_locations(entry)
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

def swap_persons(entry, used_persons, gender_detector):
    source = 'data/da-entity-names/people/'
    persons = get_people(entry)
    new_line = entry
    offset = 0

    for person in persons:
        '''
        TODO
        if persons last name in the matching keys
            1. Get the key's values last name
            2. Generate only the first names
            3. Return the name
        '''
        if person['name'] not in used_persons:
            gender = get_gender(person['name'].split()[0], gender_detector)

            # If the full name is not in the used persons dict, check for the last name
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


    #name.split()[-1]



def replace_and_save_pert(source_file, output_file, replacements_path, perturbed = False):
    source = 'data/da-entity-names'
    # names that have already been assigned and cannot be used again
    used_persons = {}
    used_locs = {}
    d = gender.Detector()

    source_path = obtain_file_path(source_file)

    with open(source_path, 'r') as f:
        while True:
            # This dictionary will serve as the new line in the new file with entities replaced
            build_replaced_line = {}
            # read a line from the source file
            try:
                line = line_to_dict(f.readline())
            except:
                return

            for key in line:
                if key == 'perturbed_answer':
                    build_replaced_line['perturbed_asnwer'] = []
                    for answer in line[key]:
                        people_changed  = swap_persons(answer, used_persons, d)
                        locs_changed    = swap_locs(people_changed, used_locs)
                        build_replaced_line['perturbed_asnwer'].append(locs_changed)
                    print(build_replaced_line)
            
            return


def replace_directory(input, output, data):
    files = [item for item in os.listdir('../' + input) if not item[0] == '.' and not item == 'README.md']
    
    for file in files:
        replace_and_save(input + '/' + file, output + '/r' + file, data)

replace_directory('TOFU', 'rTOFU', 'data/da-entity-names/')

# replace_and_save('TOFU/forget01_perturbed.json', 'test', 'data/da-entity-names/')

