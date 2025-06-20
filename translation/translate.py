from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

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

                translated_key = translate(key)
                # If the key is a list, go through each element and append them to the list
                if type(line[key]) == list:
                    build_replaced_line[key] = []
                    for answer in line[key]:
                        translated_answer = translate(answer)
                        build_replaced_line[translated_key].append(translated_answer)
                
                # Else it has just a single value
                else:
                    translated_line = translate(line[key])

                    print('AFTER: ', locs_changed)
                    build_replaced_line[translated_key] = translated_line
                print(build_replaced_line)

            line_to_write = dict_to_line(build_replaced_line) + '\n'
            #print('LINE TO WRITE: ', line_to_write)
            write_tofu(line_to_write, output_file)