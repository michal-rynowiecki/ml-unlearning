import unittest

def test_mexico():

    for i in range(100):
        import spacy
        nlp = spacy.load("en_core_web_trf")
        doc = nlp("Aurelio Beltr\u00e1n was born in Mexico City, Mexico.")

        ents = [ent.text for ent in doc.ents]
        assert 'Mexico' in ents
        assert 'Mexico City' in ents

test_mexico()