from transformers import pipeline

'''
Translate a line from source language to target language
$ line - line of text to translate
$ source - source language, i.e. the language the line is in, e.g. 'fr' for french
$ target - target language, i.e. the language the line will be translated to, e.g. 'en' for english
'''
def translate(line, translator):
    text = line
    translated_text = translator(text)[0]['translation_text']

    return translated_text
