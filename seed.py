# -*- coding: utf-8 -*-
#External libraries
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from pprint import pprint
from lxml import html
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
    countries_to_exclude = ["Hong Kong", "Macau", 
        "Christmas Island", "Cocos (Keeling) Islands", "Norfolk Island", "Greenland",
        "Republika Srpska", "Federation of Bosnia and Herzegovina", "Tokelau", 
        "\xc5land", "Aland", "Faroe Islands", "New Caledonia", "Saint Pierre and Miquelon",
        "Cyrenaica", "French Polynesia", "Wallis and Futuna", "French Southern and Antarctic Lands",
        "Azad Kashmir", "British Indian Ocean Territory", "Saint Helena, Ascension and Tristan da Cunhan",
        "Aruba", "Cook Islands", "Niue", "Akrotiri and Dhekelia", "Vatican City",
        "Guernsey", "Alderney", "Herm", "Sark", "Isle of Man", "Jersey", "Montserrat", 
        "American Samoa", "Guam", "Northern Samoa", "Northern Mariana Islands", "Puerto Rico", "U.S. Virgin Islands",
        "Marshall Islands", "Micronesia", "Palau", "Falkland Islands", "Pitcairn Islands",
        "South Georgia and the SOuth Sandwich Islands", "British Antarctic Territory",
        ]


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
        if template_name == flag:
            country = template.get(1).value
            country = translate(str(country), None, '[]')
            if '\\x' in country:
                continue
            # print country
            if country not in countries_to_exclude and country != "Abkhazia":
                countries.append(country)
            elif country == "Abkhazia":
                break
    print countries
    return countries

# def g():
#     """Alternate grab of all countries from U. S. Department of State"""
#     page = requests.get("http://www.state.gov/s/inr/rls/4250.htm")
#     tree = html.fromstring(page.text)
#     print tree



def load_country(country_name, capital):
    """Loads countries into posgreSQL Athena database"""
    if country_name == "Algeria":
        capital = "Algiers"
    if country_name == "Brazil":
        capital = "Brazilia"
    if country_name == "Bermuda":
        capital = "Hamilton"
    if country_name == "Swizterland":
        capital = "Bern"
    if country_name == "Cayman Islands":
        capital = "George Town"
    if country_name == "Cameroon":
        capital = "Yaounde"
    if country_name =="Djibouti":
        capital = "Djibouti"
    if country_name == "Cyprus":
        capital = "Nicosia"
    if country_name == "Denmark":
        capital = "Copenhagen"
    if country_name == "Ghana":
        capital = "Accra"
    if country_name == "Iceland":
        capital = "Reykjavik"
    if country_name == "Israel":
        capital = "Jerusalem"
    if country_name == "Italy":
        capital = "Rome"
    if country_name == "Jamaica":
        capital = "Kingston"
    if country_name == "Luxembourg":
        capital = "Luxembourg"
    if country_name == "Maldives":
        capital = "Male"
    if country_name == "United Kingdom":
        capital = "London"
    if country_name == "Mauritius":
        capital = "Port Louis"
    if country_name == "Moldova":
        capital = "Chisinau"
    if country_name == "Nauru":
        capital = "Yaren District"
    if country_name == "Nicaragua":
        capital = "Managua"
    if country_name == "Paraguay":
        capital = "Asuncion"
    if country_name == "Togo":
        capital = "Lome"
    if country_name == "Tonga":
        capital = "Nuku'alofa"
    if country_name == "Sri Lanka":
        capital = "Colombo"
    if country_name == "South Africa":
        capital = "Cape Town, Pretoria, Bloemfontein"
    if country_name == "Swaziland":
        capital = "Mbabane"
    if country_name == "Costa Rica":
        capital = "San Jose"
    if country_name == "Nepal":
        capital = "Kathmandu"
    if country_name == "United States":
        country_name == "United States of America"
        capital = "Washington D. C."

    country = Country(country_name=country_name, capital=capital)

    db.session.add(country)
    db.session.commit()


def get_capital(infobox_template, country_name):
    """ Isolates the infobox template, grabs the capital parameter out, and returns it.
    Helper function for get_infobox."""
    print country_name
    capital = str(infobox_template.get("capital").value) 
    print capital

    #Clean up if the capital field has an embedded template
    if mwparserfromhell.parse(capital).filter_templates() != []:
        print "yes mwparser found a buried template"
        remove = str(mwparserfromhell.parse(capital).filter_templates()[0])
        capital = capital.replace(remove, "")
        print "Removed the temlpate"
        print capital

    #Clean up if the capital has gross characters using slicing
    unwanted = ['<', '/', ',', '(', '|']
    for char in unwanted:
        print char
        if char in capital:
            print "it's in there"
            capital = capital.split(char)
            print capital
            capital = capital[0]
            print capital
            break


    capital = capital.strip('\\n')
    capital = capital.replace('\\', "")
    capital = translate(capital, None, '[]')
    capital = capital.strip()
    print capital


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

        if template.find("Infobox country") != -1:
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
    get_all_countries()
    query_countries(countries)




