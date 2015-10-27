from flask import Flask, request, render_template
from random import choice, sample
import requests
import wikipedia
import mwparserfromhell
from pprint import pprint

app = Flask(__name__)

#Imports and flask app call
##############################################################################

countries = ['kenya', 'somalia', 'nigeria', 'ethiopia']

query_params = {
    "action": "query",
    "titles": None,
    "prop": "revisions",
    "rvprop": "content",
    "format": "json",
    "formatverson": 2
    }

def get_country_infobox(country):
    """ API call to wikipedia to grab the string of JSON for the requested country.
    Uses requests to turn the string into a python dictionary and return a
    dictionary that begins at the key 'Infobox country'

    """ 
    #Query the wikipedia API for the JSON object, convert to Python dictionary
    query_params["titles"] = country
    r = requests.get("https://en.wikipedia.org/w/api.php?", params=query_params)
    info = r.json()

    #Key into the dictionary to the Infobox level
    infobox_json = str(info["query"]["pages"].values()[0]["revisions"][0])

    #Parse the dictionary and filter it by wiki template names
    wikicode = mwparserfromhell.parse(infobox_json)
    templates = wikicode.filter_templates()

    #Find the template with the string "infobox" in the name and return new dictionary
    #starting at the Infobox level, parsed again
    j = 0
    for i in templates:
        country_dict = templates[j]
        template = country_dict.name
        template = template.strip()
        if template.find("Infobox") != -1:
            print "Got the infobox"
            country_dict = mwparserfromhell.parse(country_dict)
            pprint(country_dict[1900:3000])
        j += 1




def parse_for_capital(info_file):
    """ docstring holder"""
    # for 'revisions' in r:
    pass







get_country_infobox('kenya')















##############################################################################
#Helper Functions

if __name__ == "__main__":
    #app.run(debug=True)
    pass