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

def get_country(country):
    """ API call to wikipedia to grab the string of JSON for the requested country.
    Uses requests to turn the string into a python dictionary.

    """ 
    query_params["titles"] = country
    r = requests.get("https://en.wikipedia.org/w/api.php?", params=query_params)
    info = r.json()

    print "Here is the infobox:"
    infobox_json = str(info["query"]["pages"].values()[0]["revisions"][0])
    


    # for i in infobox_json:
    #     if i == "Infobox":
    #         infobox_json[i:]
    # else:
    #     print "couldn't find the infobox"
    wikicode = mwparserfromhell.parse(infobox_json)
    templates = wikicode.filter_templates()
    j = 0
    for i in templates:
        template = templates[j].name
        tempalte = template.strip()
        template = template.split()
        print template
        if template[0] == "Infobox":
            print "Found Infobox!"
        else:
            print "No infobox yet"
        j += 1

    #     # if template.name.matches("Infobox country"):
    #     #     print "Yes!"
    # else:
    #     print "Still no infobox"




def parse_for_capital(info_file):
    """ docstring holder"""
    # for 'revisions' in r:
    pass







get_country('kenya')















##############################################################################
#Helper Functions

if __name__ == "__main__":
    #app.run(debug=True)
    pass