from flask import Flask, request, render_template
from random import choice, sample
from pprint import pprint
from string import translate
# from string import strip
import requests, wikipedia, mwparserfromhell


app = Flask(__name__)
app.secret_key = "Get up, get up, get up, it's the first of the month."

#Imports and flask app call

##############################################################################
#Static Functions

def get_capital(infobox_template, country):
    """ Isolate the infobox template, grab the capital parameter out, and return it"""
    capital = str(infobox_template.get("capital").value)
    capital = capital[:-2]                                  #come back to this, it's icky
    capital = translate(capital, None, '[]')    

    #TODO: Figure out a less brittle way to strip the \n character out.  
    #\n is not being treated as a newline, but rather 2 separate characters
    print country + ": " + capital
    return capital

##############################################################################
#App Routes

@app.route('/')
def get_quiz_questions():
    return render_template("quiz_country.html")


@app.route('/quiz')
def get_country_infobox():
    """ API call to wikipedia to grab the string of JSON for the requested country
    and return a dictionary that begins at the template/key 'Infobox country'

    """ 
    #Get country from the form:
    country = request.args.get("country")

    #Define query params
    query_params = {
    "action": "query",
    "titles": country,
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
            print "Got the infobox!\n"
            template_list = mwparserfromhell.parse(country_dict).filter_templates()
            infobox_template = template_list[0]
            capital = get_capital(infobox_template, country)
            return render_template("quiz_questions.html", country=country)
        j += 1






   
  


# get_country_infobox('kenya')
# get_country_infobox('nigeria')
# get_country_infobox('canada')
# get_country_infobox('england')















##############################################################################
#Helper Functions

if __name__ == "__main__":
    app.run(debug=True)
    



