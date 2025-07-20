from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from translator.translator import translate

from transformers import pipeline

import os

# Adjust these to change the language

SOURCE_LANGUAGE = "en"
TARGET_LANGUAGE = "da"
MODEL           = "Helsinki-NLP/opus-mt-en-da"

def translate_and_save(source_file, output_file):

    model = pipeline(f"translation_{SOURCE_LANGUAGE}_to_{TARGET_LANGUAGE}", model=MODEL, device = -1)

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
                print('before:', line)
                #translated_key = key_translations[key]
                translated_key = key
                # Since the answers are only names, dont translate them.
                if key != "question":
                    build_replaced_line[translated_key] = line
                
                # Else it has just a single value
                else:
                    translated_line = translate(line[key], model)

                    build_replaced_line[translated_key] = translated_line

            line_to_write = dict_to_line(build_replaced_line) + '\n'

            write_tofu(line_to_write, output_file)

def translate_directory(input, output):
    files = [item for item in os.listdir('../' + input) if not item[0] == '.' and not item == 'README.md']
    
    for file in files:
        translate_and_save(input + '/' + file, output + '/t' + file)

translate_and_save('TOFU/real_authors.json', 't2TOFU/authors/real_authors.json')

#translate_directory('rTOFU', 'tTOFU')