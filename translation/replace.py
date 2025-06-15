from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from NER_recognition.find_entities import get_people, get_locations
from write_translations.replacements import add_matching

def replace_and_save(source_file, output_file, replacements_path):
    # names that have already been assigned and cannot be used again
    used_persons = {}
    used_locs = {}

    source_path = obtain_file_path(source_file)

    with open(source_path, 'r') as f:
        while True:
            # This dictionary will serve as the new line in the new file with entities replaced
            build_replaced_line = {}
            # read a line from the source file
            line = line_to_dict(f.readline())
            if not line: 
                return
            
            # For every value in the dictionary from the json file single line iterate through
            # its text value and replace their contents
            for key in line:
                new_line = line[key]
                locations = get_locations(line[key])
                persons = get_people(line[key])

                # TODO make this a function
                
                # Add matchings for each of the locations in the line
                for location in locations:
                    # If location is a country then just assign Denmark to it
                    if location['type'] == 'country':
                        used_locs[location['name']] = 'Denmark'
                    
                    # Otherwise, assign a random city from list of cities 
                    elif location['name'] not in used_locs:
                        add_matching(used_locs, location['name'], 'data/da-entity-names/CITY.txt')

                    # Each time when changing a location or an entity, the length of the line changes
                    # , so its necassary to offset the start and end of the entity in the line
                    offset = len(line[key]) - len(new_line)
                    start_loc   = location['start_c'] - offset
                    finish_loc  = location['end_c'] - offset
                    
                    # Create the new line by cutting out the old entity and adding in the new one
                    new_line = new_line[:start_loc] + used_locs[location['name']] + new_line[finish_loc:]


                # TODO make this into a function

                # Add matchings for each of the locations in the line
                for person in persons:
                    
                    # Otherwise, assign a random city from list of cities 
                    if person['name'] not in used_persons:
                        add_matching(used_persons, person['name'], 'data/da-entity-names/PER.txt')

                    # Each time when changing a location or an entity, the length of the line changes
                    # , so its necassary to offset the start and end of the entity in the line
                    offset = len(line[key]) - len(new_line)
                    start_loc   = person['start_c'] - offset
                    finish_loc  = person['end_c'] - offset
                    
                    # Create the new line by cutting out the old entity and adding in the new one
                    new_line = new_line[:start_loc] + used_persons[person['name']] + new_line[finish_loc:]

                build_replaced_line[key] = new_line

            
            print(build_replaced_line)
            line_to_write = dict_to_line(build_replaced_line) + '\n'
            write_tofu(line_to_write, 'rTOFU/rforget01.json')


replace_and_save('TOFU/forget01.json', 'rTOFU/rforget01.json', 'data/da-entity-names/PER.txt')