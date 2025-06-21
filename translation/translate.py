from read_data.get_TOFU import obtain_file_path, line_to_dict
from save_data.save_TOFU import dict_to_line, write_tofu

from translator.translator import translate

from transformers import pipeline

# Adjust these to change the language

SOURCE_LANGUAGE = "en"
TARGET_LANGUAGE = "da"
MODEL           = "Helsinki-NLP/opus-mt-en-da"

def translate_and_save(source_file, output_file):

    model = pipeline(f"translation_{SOURCE_LANGUAGE}_to_{TARGET_LANGUAGE}", model=MODEL)

    # key translations, so that they don't have to be translated for every line, also perturbed is difficult to translated
    key_translations = {"question": "spørgsmål", 
    "answer": "svar", 
    "perturbed_answer": "forstyrret_svar", 
    "paraphrased_question": "omskrevet_spørgsmål",
    "paraphrased_answer": "omskrevet_svar"}

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
            
            print('BEFORE: ', line)
            # For every value in the dictionary from the json file single line iterate through
            # its text value and replace their contents
            for key in line:

                translated_key = key_translations[key]
                # If the key is a list, go through each element and append them to the list
                if type(line[key]) == list:
                    build_replaced_line[translated_key] = []
                    for answer in line[key]:
                        translated_answer = translate(answer, model)
                        build_replaced_line[translated_key].append(translated_answer)
                
                # Else it has just a single value
                else:
                    translated_line = translate(line[key], model)

                    build_replaced_line[translated_key] = translated_line
                print(build_replaced_line)

            line_to_write = dict_to_line(build_replaced_line) + '\n'
            print('AFTER: ', line_to_write)
            write_tofu(line_to_write, output_file)

def translate_directory(input, output, data):
    files = [item for item in os.listdir('../' + input) if not item[0] == '.' and not item == 'README.md']
    
    for file in files:
        translate_and_save(input + '/' + file, output + '/r' + file, data)

translate_and_save('rTOFU/rforget01_perturbed.json', 'tTOFU/tforget_perturbed01.json')