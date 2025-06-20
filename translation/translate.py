from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from NER_recognition.find_entities import get_people, get_locations, random_name, get_gender, random_city
from write_translations.replacements import add_matching

def replace_and_save(source_file, output_file, replacements_path, perturbed = False):
    # names that have already been assigned and cannot be used again

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
                if type(line[key]) == list:
                    build_replaced_line[key] = []
                    translated_key = translate(key)
                    for answer in line[key]:
                        
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