from flask import Flask, request, render_template
from random import choice, sample
from pprint import pprint
# from string import strip
import requests, wikipedia, mwparserfromhell, string


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
            print "Got the infobox!\n"
            template_list = mwparserfromhell.parse(country_dict).filter_templates()
            infobox_template = template_list[0]
            parse_for_capital(infobox_template)
        j += 1
        


def parse_for_capital(infobox_template):
    """ Isolate the infobox template, grab the capital parameter out, and return it"""
    capital = str(infobox_template.get("capital").value)
    capital = capital.strip('\n')                    #can't strip \newline
    capital = string.translate(capital, None, '[]')
    
    print capital
  


get_country_infobox('kenya')
get_country_infobox('nigeria')
get_country_infobox('canada')
get_country_infobox('england')















##############################################################################
#Helper Functions

if __name__ == "__main__":
    #app.run(debug=True)
    pass