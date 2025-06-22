import spacy
import geonamescache
import pandas as pd
import numpy as np
import gender_guesser.detector as gender
import random

'''
The available tags can be 
found on https://spacy.io/models/en in label scheme, and explained by
running spacy.explain(TAG)

FAC: buildings, airports, highways, bridges etc.
GPE: countries, cities, states
LOC: non-GPE locations, mountain ranges, bodies of water
NORP: nationalities or religous or political groups
ORG: companies, agencies, institutions, etc. 
'''

'''
Creates a list of persons present in the line
'''
def get_people(line: str, model) -> list:
    nlp = model
    doc = nlp(line)

    people = []
    # Go through each recognized entity
    for entity in doc.ents:
        label = entity.label_
        # Only proceed if the entity is a person
        if entity.label_ == "PERSON":
            # Get required values from each recognized person
            name = entity.text
            start = entity.start_char
            end = entity.end_char
            
            # if entity ends with a possessive suffix ('s), remove it and change end char by -2
            if entity.text[-2:] == '\'s':
                name = name[:-2]
                end -= 2

            people.append({"name": name, "start_c": start, "end_c": end, "type": label})
        
        elif entity.label == "NORP":
            nationality = entity.text
            start = entity.start_char
            end = entity.end_char

            people.append({"name": name, "start_c": start, "end_c": end, "type": label})

    # Return a tuple with the values
    return people


'''
Creates a list of locations present in the line. Merges locations of type (city, country) into (city)
'''
def get_locations(line: str, model) -> list:
    nlp = model
    doc = nlp(line)
    

    locations = []
    # Go through each recognized entity
    for entity in doc.ents:
        # Only proceed if the entity is a location
        if entity.label_ in ('FAC', 'GPE', 'LOC', 'ORG'):
            # Get required values from each recognized location
            name = entity.text
            start = entity.start_char
            end = entity.end_char
            
            # Get type of location
            label = entity.label_

            # if entity ends with a possessive suffix ('s), remove it and change end char by -2
            if entity.text[-2:] == '\'s':
                name = name[:-2]
                end -= 2

            locations.append({"name": name, "type": label, "start_c": start, "end_c": end})

    
    # Check if there are any locations of the form (city, country), and if so, adjust labels
    new_locations = cities_countries(locations)

    return new_locations


'''
Takes in a list of locations and detects if two locations are within a space of
each other. If so, they are merged into a single location
'''
def cities_countries(locations: list) -> list:
    
    # Get a list of existing countries and some cities
    gc = geonamescache.GeonamesCache()
    countries = [country['name'] for country in gc.get_countries().values()]
    cities = [city['name'] for city in gc.get_cities().values()]


    for location in locations:
        if location['name'] in countries:
            location['type'] = 'country'
        elif location['name'] in cities:
            location['type'] = 'city'
        # This is the case if it is a City, Country recognized as just the city
        elif location['type'] == 'GPE':
            actual_city = location['name'].split(',')[0]
            location['name'] = actual_city
            location['type'] = 'city'

    return locations

'''
Creates a random name from provided path
$ gender
    m - men
    f - female
    TODO
    n - other
'''
def random_name(source, gender = 0, last_name=True):
    # Read in the data
    
    surname = pd.read_excel('../' + source + 'prsurnames.xlsx')
    match gender:
        case 'm':
            df = pd.read_excel('../' + source + 'prPER_boys.xlsx')
        case 'f':
            df = pd.read_excel('../' + source + 'prPER_girls.xlsx')
    
    first, middle, middle2 = np.random.choice(a=df["name"], size=3, replace=False, p=df['probability'])
    
    first = first.lower().capitalize()
    middle = middle.lower().capitalize()
    middle2 = middle.lower().capitalize()

    last, last2 = np.random.choice(a=surname["name"], size=2, replace=False, p=surname['probability'])[0:2]

    # Determine the number of names:
    nm = random.random()
    if nm <= 0.55:
        nm = 3
    elif nm <= 0.83:
        nm = 2
    else:
        nm = 4

    match nm:
        case 3:
            if last_name:
                full_name = f"{first} {middle} {last}"
            else:
                full_name = f"{first} {middle}"
        case 2:
            if last_name:
                full_name = f"{first} {last}"
            else:
                full_name = f"{first}"
        case 4:
            if last_name:
                full_name = f"{first} {middle} {last}-{last2}"
            else:
                full_name = f"{first} {middle}"

    return full_name

def random_city(source):
    cities = pd.read_excel('../' + source + 'prPER_city.xlsx')
    city = np.random.choice(a=cities["city"], size=1, replace=False, p=cities['probability'])[0]
    return city

def get_gender(name, detector):
    guess = detector.get_gender(name)

    if guess == 'male' or guess == 'mostly_male':
        return 'm'
    elif guess == 'female' or guess == 'mostly_female':
        return 'f'
    else:
        return 'm' if round(random.random())  else 'f'


