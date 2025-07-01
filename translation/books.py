from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from translator.translator import translate

from transformers import pipeline

import os
import re
import string

# Adjust these to change the language
SOURCE_LANGUAGE = "en"
TARGET_LANGUAGE = "da"
MODEL           = "Helsinki-NLP/opus-mt-en-da"


def translate_book_and_save(source_file, output_file):

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

                # If the key is a list, go through each element and append them to the list
                if type(line[key]) == list:
                    print('Line list: ', line[key])
                    build_replaced_line[key] = []
                    for answer in line[key]:
                        
                        # Find all the titles in a particular line
                        titles = get_titles(answer)

                        # Create a dictionary with a translation for each title
                        translation_dict = {}
                        for title in titles:
                            translation_dict[title] = translate(title, model)

                        # Create a new line by replacing original titles with translated titles
                        new_line = answer
                        for item in translation_dict:
                            new_line = new_line.replace(item, translation_dict[item])


                        build_replaced_line[key].append(new_line)
                
                # Else it has just a single value
                else:
                    # Find all the titles in a particular line
                    titles = get_titles(line[key])

                    # Create a dictionary with a translation for each title
                    translation_dict = {}
                    for title in titles:
                        translation_dict[title] = translate(title, model)

                    # Create a new line by replacing original titles with translated titles
                    new_line = line[key]
                    for item in translation_dict:
                        new_line = new_line.replace(item, translation_dict[item])                  
                    
                    
                    build_replaced_line[key] = new_line
                

            line_to_write = dict_to_line(build_replaced_line) + '\n'

            write_tofu(line_to_write, output_file)


def get_titles(line):
    pattern = r'\\"(.*?)\\"|"(.*?)"|\'(.*?)\''

    matches = re.findall(pattern, line)

    # Flatten and filter only the non-empty match from each tuple
    raw_matches = [next(m for m in group if m) for group in matches]

    # Clean up punctuation and spaces
    cleaned_matches = [m.strip(string.punctuation + " ") for m in raw_matches]

    # Remove all the contractions ('m, 's, 're)
    cleaned = [item for item in cleaned_matches if not re.match(r"['\"]?[s]", item)]
    cleaned = [item for item in cleaned if not re.match(r"['\"]?[m]", item)]
    cleaned = [item for item in cleaned if not re.match(r"['\"]?[r]", item)]

    return list(set(cleaned))

def replace_book_directory(input, output, data):

    files = [item for item in os.listdir('../' + input) if not item[0] == '.' and not item == 'README.md' and not 'real' in item and not 'facts' in item]
    
    for file in files:
        translate_book_and_save(input + '/' + file, output + '/b' + file, data)

translate_book_and_save('tTOFU/forget01.json', 'bTOFU/bforget01.json')