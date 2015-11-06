# -*- coding: utf-8 -*-
#External libraries
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from pprint import pprint
from lxml import html
from string import translate, lower
import requests, wikipedia, mwparserfromhell
import io

#Internal files
from model import connect_to_db, db, User, Continent, Country
from server import app

##############################################################################
# Seed the database with country information


# def get_all_countries():
#     """Queries Wikipedia's List of Sovereign States page for all current countries"""
#     #Query the wikipedia API for the JSON object, convert to Python dictionary and key down to the meat of it
#     countries_to_exclude = ["Hong Kong", "Macau", "Reunion", "Saint Helena, Ascension and Tristan da Cunha", 
#         "Christmas Island", "Akrotiri and Dhekelia", "S\xe3o Tom\xe9 and Pr\xedncipe", "Cocos (Keeling) Islands", "Norfolk Island", "Greenland",
#         "Republika Srpska", "Federation of Bosnia and Herzegovina", "Tokelau", 
#          "Aland", "Faroe Islands", "New Caledonia", "Saint Pierre and Miquelon",
#         "Cyrenaica", "French Polynesia", "Wallis and Futuna", "French Southern and Antarctic Lands",
#         "Azad Kashmir", "British Indian Ocean Territory", "Saint Helena, Ascension and Tristan da Cunhan",
#         "Aruba", "Cook Islands", "Niue", "Akrotiri and Dhekelia", "Vatican City", "Gibraltar", "Guernsey",
#         "Guernsey", "Alderney", "Herm", "Sark", "Isle of Man", "Jersey", "Montserrat", 
#         "American Samoa", "Guam", "Northern Samoa", "Northern Mariana Islands", "Puerto Rico", "U.S. Virgin Islands",
#         "Marshall Islands", "Micronesia", "Palau", "Falkland Islands", "Pitcairn Islands", "French Southern Territories", 
#         "South Georgia and the SOuth Sandwich Islands", "Heard Island and McDonald Islands", "Wake Island", "Bouvet Island", "British Antarctic Territory", "South Georgia and the South Sandwich Islands",
#         "British Indian Ocean Territory", "Christmas Island", "Cocos (Keeling) Islands", "Timor-Leste",
#         "Nagorno-Karabakh", "Northern Cyprus", "South Ossetia", "Jersey", "Svalbard", "Transnistria", "Anguilla", 
#         "Bermuda", "Bonaire", "British Virgin Islands", "Cayman Islands", "Clipperton Island", "Curacao", "Greenland", "Guadeloupe",
#         "Martinique", "Montserrat", "Navassa Island", "Saint Barthelemy", "Saint Martin", 
#         "Sint Eustatius", "Sint Maarten", "Turks and Caicos Islands", "United States Virgin Islands", "South Georgia and the South Sandwish Islands",
#         "American Samoa", "Ashmore and Cartier Islands", "Cook Islands", "Baker Island", "Coral Sea Islands", 
#         "Guam", "Howland Island", "Jarvis Island", "Johnston Atoll", "Kingman Reef", "Midway Atoll",  
#         "Niue", "Norfolk Island", "Northern Mariana Islands", "Palmyra Atoll", 
#         "French Guiana", "Mayotte", "Sahrawi Arab Democratic Republic",
#         "Bouvet Island", "French Southern and Antarctic Lands", "Heard Island and McDonald Islands"
#         ]

#     countries = []

#     r = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&utf8&rvprop=content&titles=list%20of%20sovereign%20states%20and%20dependent%20territories%20by%20continent")
#     info = r.json()
#     country_info = str(info["query"]["pages"].values()[0]["revisions"][0])

#     #Parse into wiki templates
#     flag = "flagicon"
#     wikicode = mwparserfromhell.parse(country_info)
#     templates = wikicode.filter_templates()

#     for template in templates:
#     #Search the templates with flag in the name for the country name, store in list
#         template_name = (template.name)
#         if flag in template_name:
#     #         #Check if they aren't sovereign states or associated states
#             if template.get(1).value:
#                 country = template.get(1).value
#                 # country = translate(str(country), None, '[]')

#             if country not in countries_to_exclude and "\\x" not in country:
#                 countries.append(country)
#     print countries
#     print len(countries)


#     return countries



# def load_country(country_name, capital):
#     """Loads countries into posgreSQL Athena database"""
#     if country_name == "Algeria":
#         capital = "Algiers"
#     if country_name == "Brazil":
#         capital = "Brazilia"
#     if country_name == "Bermuda":
#         capital = "Hamilton"
#     if country_name == "Swizterland":
#         capital = "Bern"
#     if country_name == "Cayman Islands":
#         capital = "George Town"
#     if country_name == "Cameroon":
#         capital = "Yaounde"
#     if country_name =="Djibouti":
#         capital = "Djibouti"
#     if country_name == "Cyprus":
#         capital = "Nicosia"
#     if country_name == "Denmark":
#         capital = "Copenhagen"
#     if country_name == "Ghana":
#         capital = "Accra"
#     if country_name == "Iceland":
#         capital = "Reykjavik"
#     if country_name == "Israel":
#         capital = "Jerusalem"
#     if country_name == "Italy":
#         capital = "Rome"
#     if country_name == "Jamaica":
#         capital = "Kingston"
#     if country_name == "Luxembourg":
#         capital = "Luxembourg"
#     if country_name == "Maldives":
#         capital = "Male"
#     if country_name == "United Kingdom":
#         capital = "London"
#     if country_name == "Mauritius":
#         capital = "Port Louis"
#     if country_name == "Moldova":
#         capital = "Chisinau"
#     if country_name == "Nauru":
#         capital = "Yaren District"
#     if country_name == "Nicaragua":
#         capital = "Managua"
#     if country_name == "Paraguay":
#         capital = "Asuncion"
#     if country_name == "Togo":
#         capital = "Lome"
#     if country_name == "Tonga":
#         capital = "Nuku'alofa"
#     if country_name == "Sri Lanka":
#         capital = "Colombo"
#     if country_name == "South Africa":
#         capital = "Cape Town, Pretoria, Bloemfontein"
#     if country_name == "Swaziland":
#         capital = "Mbabane"
#     if country_name == "Costa Rica":
#         capital = "San Jose"
#     if country_name == "Nepal":
#         capital = "Kathmandu"
#     if country_name == "United States":
#         country_name == "United States of America"
#         capital = "Washington D. C."

#     country = Country(country_name=country_name, capital=capital)
#     db.session.add(country)
#     db.session.commit()



# def get_capital(infobox_template, country_name):
#     """ Isolates the infobox template, grabs the capital parameter out, and returns it.
#     Helper function for get_infobox."""
#     print country_name
#     capital = str(infobox_template.get("capital").value) 
#     print capital

#     #Clean up if the capital field has an embedded template
#     # if mwparserfromhell.parse(capital).templates() != []:
#     #     print "yes mwparser found a buried template"
#     #     remove = str(mwparserfromhell.parse(capital).filter_templates()[0])
#     #     capital = capital.replace(remove, "")
#     #     print "Removed the template"
#     #     print capital

#     #Clean up if the capital has gross characters using slicing
#     unwanted = ['<', '/', ',', '(', '|']
#     for char in unwanted:
#         if char in capital:
#             print "it's in there"
#             capital = capital.split(char)
#             print capital
#             capital = capital[0]
#             print capital


#     capital = capital.strip()
#     capital = capital.replace('\\', "")
#     capital = translate(capital, None, '[]')
#     capital = capital.strip()
#     print capital


#     print country_name + ": " + capital
#     return capital


# def get_infobox(country_name):
#     """ API call to wikipedia. Grabs a country's name and capital and 
#     calls load_country on them
#     """
#     #Define query params
#     query_params = {
#     "action": "query",
#     "titles": country_name,
#     "prop": "revisions",
#     "rvprop": "content",
#     "format": "json",
#     "formatverson": 2
#     }

#     #Query the wikipedia API for the JSON object, convert to Python dictionary
#     r = requests.get("https://en.wikipedia.org/w/api.php?", params=query_params)
#     info = r.json()

#     #Key into the dictionary to the Infobox level
#     infobox_json = str(info["query"]["pages"].values()[0]["revisions"][0])

#     #Parse the dictionary and filter it by wiki template names
#     wikicode = mwparserfromhell.parse(infobox_json)
#     templates = wikicode.filter_templates()
#     #Find the template with the string "infobox" in the name and return new dictionary
#     #starting at the Infobox level, parsed again
#     j = 0
#     for i in templates:
#         country_dict = templates[j]
#         template = country_dict.name
#         template = template.strip()

#         if template.find("Infobox country") != -1:
#             template_list = mwparserfromhell.parse(country_dict).filter_templates()
#             infobox_template = template_list[0]
#             capital = get_capital(infobox_template, country_name)
#             load_country(country_name, capital)
#         j += 1

# def query_countries(country_list):
#     """Takes a list of countries and calls get_infobox on each of them."""
#     for country in country_list:
#         country = str(country)
#         get_infobox(country)



def get_continents():
    """Seeds database manually with the 7-continent model."""
    continents = ['North America', 'South America', 'Africa', 'Europe', 'Asia', 'Oceania', 'Antarctica']
    for i in continents:
        print i
        continent = Continent(name=i)
        print continent
        db.session.add(continent)
    db.session.commit()


def get_africa():
    """Query the RESTCountries API and get country, capital, primary language ISO code, demonym, and region"""
    #Define query params
    r = requests.get("https://restcountries-v1.p.mashape.com/region/africa",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    info = r.json()
    for country_dict in info:
        name = country_dict["name"]
        alpha_code = country_dict["alpha3Code"]
        demonym = country_dict["demonym"]
        region = country_dict["region"]
        capital = country_dict["capital"]
        lang_list = []

        iso_list = country_dict["languages"]
        for lang in iso_list:
            lang = str(lang)
            lang = translate_lang(lang)
            lang_list.append(lang)

        country = Country(
            country_name=name, 
            alpha_code=alpha_code, 
            demonym=demonym,
            continent_name=region,
            languages=lang_list,
            capital=capital
            )
        print country
        print country.languages


def make_iso_lang_dict():
    """Build an ISO language code dictionary."""
    iso_langs = {}
    iso_txt = io.open("iso_codes.txt", 'w', encoding='utf8')
    for line in iso_txt:
        line = line.strip()
        line = line.split("|")
        code = line[2]
        country = line[3]
        iso_langs[code] = country
    return iso_langs
iso_langs = make_iso_lang_dict()


def translate_lang(code):
    """Translate an ISO language code to a language text name."""
    language = iso_langs[code]
    return language




if __name__ == "__main__":
    connect_to_db(app)

#     # In case tables haven't been created, create them
    db.create_all()

#     # Kick off the API calls, seed the databsase
    # get_continents()
    # countries = get_all_countries()
    # query_countries(countries)




