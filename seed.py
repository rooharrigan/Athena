# -*- coding: utf-8 -*-
#External libraries
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from pprint import pprint
from lxml import html
from string import translate, lower
import requests, wikipedia, mwparserfromhell


#Internal files
from model import connect_to_db, db, User, Continent, Country
from server import app

##############################################################################
# Seed the database with country information

countries_to_exclude = ["Hong Kong", "Macau", "Reunion", "Saint Helena, Ascension and Tristan da Cunha", 
    "Christmas Island", "Akrotiri and Dhekelia", "S\xe3o Tom\xe9 and Pr\xedncipe", "Cocos (Keeling) Islands", "Norfolk Island", "Greenland",
    "Republika Srpska", "Federation of Bosnia and Herzegovina", "Tokelau", 
     "Aland", "Faroe Islands", "New Caledonia", "Saint Pierre and Miquelon",
    "Cyrenaica", "French Polynesia", "Wallis and Futuna", "French Southern and Antarctic Lands",
    "Azad Kashmir", "British Indian Ocean Territory", "Saint Helena, Ascension and Tristan da Cunhan",
    "Aruba", "Cook Islands", "Niue", "Akrotiri and Dhekelia", "Vatican City", "Gibraltar", "Guernsey",
    "Guernsey", "Alderney", "Herm", "Sark", "Isle of Man", "Jersey", "Montserrat", 
    "American Samoa", "Guam", "Northern Samoa", "Northern Mariana Islands", "Puerto Rico", "U.S. Virgin Islands",
    "Marshall Islands", "Micronesia", "Palau", "Falkland Islands", "Pitcairn Islands", "French Southern Territories", 
    "South Georgia", "Heard Island and McDonald Islands", "Wake Island", "Bouvet Island", "British Antarctic Territory", "South Georgia and the South Sandwich Islands",
    "British Indian Ocean Territory", "Christmas Island", "Cocos (Keeling) Islands", "Timor-Leste",
    "Nagorno-Karabakh", "Northern Cyprus", "South Ossetia", "Jersey", "Svalbard", "Transnistria", "Anguilla", 
    "Bermuda", "Bonaire", "British Virgin Islands", "Cayman Islands", "Clipperton Island", "Curacao", "Greenland", "Guadeloupe",
    "Martinique", "Montserrat", "Navassa Island", "Saint Barthelemy", "Saint Martin", 
    "Sint Eustatius", "Sint Maarten", "Turks and Caicos Islands", "United States Virgin Islands", "South Georgia and the South Sandwish Islands",
    "American Samoa", "Ashmore and Cartier Islands", "Cook Islands", "Baker Island", "Coral Sea Islands", 
    "Guam", "Howland Island", "Jarvis Island", "Johnston Atoll", "Kingman Reef", "Midway Atoll",  
    "Niue", "Norfolk Island", "Northern Mariana Islands", "Palmyra Atoll", 
    "French Guiana", "Mayotte", "Sahrawi Arab Democratic Republic", "Curaçao",
    "Bouvet Island", "French Southern and Antarctic Lands", "Heard Island and McDonald Islands", "Saint Helena",
    "São Tomé and Príncipe", "Réunion", "Åland Islands", "Saint Barthélemy", "United States Minor Outlying Islands", "Svalbard and Jan Mayen" 
    ]


def get_continents():
    """Seeds database manually with the 7-continent model."""
    continents = ['North America', 'South America', 'Africa', 'Europe', 'Asia', 'Oceania', 'Antarctica', 'Caribbean']
    for i in continents:
        print i
        continent = Continent(name=i)
        print continent
        db.session.add(continent)
    db.session.commit()


def get_oceania():
    "Create request object and region string for Oceania."
    r = requests.get("https://restcountries-v1.p.mashape.com/region/oceania",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    region = "Oceania"
    get_countries(r, region)


def get_americas():
    "Create request object and region string for the Americas."
    r = requests.get("https://restcountries-v1.p.mashape.com/region/americas",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    region = "Americas"
    get_countries(r, region)


def get_europe():
    "Create request object and region string for Europe."
    r = requests.get("https://restcountries-v1.p.mashape.com/region/europe",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    region = "Europe"
    get_countries(r, region)


def get_africa():
    "Create request object and region string for Africa."
    r = requests.get("https://restcountries-v1.p.mashape.com/region/africa",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    region = "Africa"
    get_countries(r, region)


def get_asia():
    "Create request object and region string for Asia."
    r = requests.get("https://restcountries-v1.p.mashape.com/region/asia",
        headers={
            "X-Mashape-Key": "vNDpoJET9amshdFf2U8wswpEdt13p1SPHWDjsnKA9N4uTmIPgu",
            "Accept": "application/json"
            }
        )
    region = "Asia"
    get_countries(r, region)


def get_countries(r, region):
    """Query the RESTCountries API, get country-related information back, and
    commit it to the database.  Takes a request object and a region string, like "Africa"."""
    info = r.json()
    for country_dict in info:
        name = country_dict["name"]
        name = name.encode('utf-8', 'ignore')
        alpha_code = country_dict["alpha3Code"]
        demonym = country_dict["demonym"]
        subregion = country_dict["subregion"]
        if region == "Americas":
            if subregion == "Northern America" or subregion == "Central America":
                new_region = "North America"
            else:
                new_region = subregion
        else:
            new_region = region
        capital = country_dict["capital"]
        lang_list = []

        iso_list = country_dict["languages"]
        for lang in iso_list:
            lang = lang.encode('utf-8', 'ignore')
            lang = translate_lang(lang)
            lang_list.append(lang)

        if name not in countries_to_exclude:
            country = Country(
                country_name=name, 
                alpha_code=alpha_code, 
                demonym=demonym,
                continent_name=new_region,
                languages=lang_list,
                capital=capital
                )
            db.session.add(country)
    db.session.commit()


def make_iso_lang_dict():
    """Builds an ISO 2-character language code dictionary."""
    iso_langs = {}
    iso_txt = open("iso_codes.txt")
    for line in iso_txt:
        line = line.strip()
        line = line.split("|")
        code = line[2]
        lang = line[3]
        iso_langs[code] = lang
    return iso_langs
iso_langs = make_iso_lang_dict()


def translate_lang(code):
    """Translates a two-character ISO language code to a language text name."""
    language = iso_langs[code]
    return language


if __name__ == "__main__":
    connect_to_db(app)

# In case tables haven't been created, create them
    db.create_all()

# Kick off the API calls, seed the databsase
    get_continents()
    get_oceania()
    get_africa()
    get_europe()
    get_asia()
    get_americas()

    




