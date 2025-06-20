# TODO make a function that reduces the doubling in the code. 

from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from NER_recognition.find_entities import get_people, get_locations, random_name, get_gender
from write_translations.replacements import add_matching

import gender_guesser.detector as gender

def replace_and_save(source_file, output_file, replacements_path):
    source = 'data/da-entity-names/people/'
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

                people_changed  = swap_persons(line[key], used_persons, d)
                locs_changed    = swap_locs(people_changed, used_locs)

                print('AFTER: ', locs_changed)
                build_replaced_line[key] = locs_changed
                #print(build_replaced_line)

            line_to_write = dict_to_line(build_replaced_line) + '\n'
            #print('LINE TO WRITE: ', line_to_write)
            write_tofu(line_to_write, 'rTOFU/rforget01.json')

# For each entry in the line dictionary
# $ entry: line of text for which entities will be swapped
# $ used_locs: dictionary of locations with which to replace
def swap_locs(entry, used_locs):
    locations = get_locations(entry)
    new_line = entry
    offset = 0

    # Get replacements for locations
    for location in locations:
        if location['type'] == 'country':
            used_locs[location['name']] = 'Denmark'
        elif location['name'] not in used_locs and location['type'] == 'city':
            add_matching(used_locs, location['name'], 'Aarhus')
        
        if location['type'] == 'country' or location['type'] == 'city':
            start_loc   = location['start_c'] - offset
            finish_loc  = location['end_c'] - offset

            offset = len(location['name']) - len(used_locs[location['name']])
            # Create the new line by cutting out the old entity and adding in the new one
            new_line = new_line[:start_loc] + used_locs[location['name']] + new_line[finish_loc:]
        else:
            1
            #TODO
    
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
def last_name(name: str, gender, used_persons: dict):
    source = 'data/da-entity-names/people/'

    last_name = name.split()[-1]
    for existing_name in used_persons.keys():
        if last_name in existing_name:
            replacement_last_name = used_persons[existing_name].split()[-1]
            new_name = random_name(source, gender, last_name=False) + ' ' + replacement_last_name
            print(new_name)


    #name.split()[-1]
for i in range(100):
    last_name('Basil Joshua Ashmadi-Al-Haran', 'm', {'Jessica Ashmadi-Al-Haran': 'Anna Smith', 'Albert Johns': 'Stone'})


# print(swap_persons("Basil Mahfouz Al-Kuwaiti was born in Basil Mahfouz Al-Kuwaiti Kuwait City, Kuwait. Basil Mahfouz Al-Kuwaiti", {}))


#replace_and_save('TOFU/forget01_perturbed.json', 'rTOFU/rforget01_perturbed.json', 'data/da-entity-names/PER.txt')

