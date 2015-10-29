#External libraries
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from pprint import pprint
from string import translate, lower
import requests, wikipedia, mwparserfromhell

#Internal files
from model import connect_to_db, db, Country, User
from server import app

##############################################################################
# Seed the database with country information

countries = []

def get_all_countries():
    """Queries Wikipedia's List of Sovereign States page for all current countries"""

    #Query the wikipedia API for the JSON object, convert to Python dictionary and key down to the meat of it
    r = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&rvprop=content&titles=list%20of%20sovereign%20states")
    info = r.json()
    country_info = str(info["query"]["pages"].values()[0]["revisions"][0])

    #Parse into wiki templates
    flag = "flag"
    wikicode = mwparserfromhell.parse(country_info)
    templates = wikicode.filter_templates()

    #Search the templates with flag in the name for the country name, store in list
    for template in templates:
        template_name = str(template.name)
        if flag in template_name:
            country = template.get(1).value
            countries.append(country)

    return countries


def load_country(country_name, capital):
    """Loads countries into posgreSQL Athena database"""
    country = Country(country_name=country_name, capital=capital)

    db.session.add(country)
    db.session.commit()


def get_capital(infobox_template, country_name):
    """ Isolates the infobox template, grabs the capital parameter out, and returns it.
    Helper function for get_infobox."""
    capital = str(infobox_template.get("capital").value)  
    capital = capital.strip('\\n')
    capital = translate(capital, None, '[]')    

    print country_name + ": " + capital
    return capital


def get_infobox(country_name):
    """ API call to wikipedia. Grabs a country's name and capital and 
    calls load_country on them
    """
    #Define query params
    query_params = {
    "action": "query",
    "titles": country_name,
    "prop": "revisions",
    "rvprop": "content",
    "format": "json",
    "formatverson": 2
    }

    #Query the wikipedia API for the JSON object, convert to Python dictionary
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
            template_list = mwparserfromhell.parse(country_dict).filter_templates()
            infobox_template = template_list[0]
            capital = get_capital(infobox_template, country_name)
            load_country(country_name, capital)
        j += 1


def query_countries(country_list):
    """Takes a list of countries and calls get_infobox on each of them."""
    for country in country_list:
        get_infobox(country)


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Kick off the API calls, seed the databsase
    query_countries(countries)

