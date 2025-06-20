from transformers import M2M100ForConditionalGeneration
from tokenization_small100 import SMALL100Tokenizer

'''
Translate a line from source language to target language
$ line - line of text to translate
$ source - source language, i.e. the language the line is in, e.g. 'fr' for french
$ target - target language, i.e. the language the line will be translated to, e.g. 'en' for english
'''
def translate(line, source, target):
    text = line

    model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100")
    tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100")

    # Translate to target language