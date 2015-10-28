from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from functools import wraps
from random import choice, sample
from pprint import pprint
from string import translate, lower
# from string import strip
import requests, wikipedia, mwparserfromhell


app = Flask(__name__)
app.secret_key = "Get up, get up, get up, it's the first of the month."

#Imports and flask app call

##############################################################################
#Static Functions

# def get_all_countries():
#     #Define query params where titles = "list of sovereign states"
#     query_params = {
#     "action": "query",
#     "titles": "list of sovereign states",
#     "prop": "revisions",
#     "rvprop": "content",
#     "format": "json",
#     "formatverson": 2
#     }

#     #Query the wikipedia API for the JSON object, convert to Python dictionary
#     r = requests.get("https://en.wikipedia.org/w/api.php?", params=query_params)
#     country_info = r.json()

#     #Search the templates named flag for the country name, store in dictionary
#     countries = {}

#     wikicode = mwparserfromhell.parse(country_info)
#     templates = wikicode.filter_templates()
#     print wikicode
#     print "##############################################"
#     print templates
     



def get_capital(infobox_template, country):
    """ Isolate the infobox template, grab the capital parameter out, and return it"""
    capital = str(infobox_template.get("capital").value)  
    capital = capital.strip('\\n')
    capital = translate(capital, None, '[]')    

    print country + ": " + capital
    return capital

##############################################################################
#App Routes

@app.route('/')
def get_quiz_questions():
    """Handles login and returns the homepage"""
    if 'username' in session:
        print 'Logged in as {}'.format(escape(session['username']))
    else:
        print "User is not logged in"

    return render_template("quiz_country.html")

@app.route('/login', methods=["POST"])
def login():
    print "login is running!"
    email = request.form.get("email")
    password = request.form.get("password")
    print "email: ", email
    password = request.form.get("password")
    print "password ", password

    if email:
        session['username'] = email
        session['password'] = password
        print session
        print "user is logged in"
        return  redirect("/")


@app.route('/logout', methods=["POST"])
def logout():
    logout = request.form.get("logout")
    if logout:
        print "Log the user out!"

    return redirect("/")


@app.route('/quiz')
def get_country_infobox():
    """ API call to wikipedia to grab the string of JSON for the requested country
    and return a dictionary that begins at the template/key 'Infobox country'

    """ 
    #Get country from the form and check that it's a country, and uppercase the first letter:
    country = request.args.get("country")
    country = country.title()


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
        else:
            print "No infobox yet."
        j += 1


@app.route('/quiz_score')
def grade_quiz():
    pass


@app.route('/percentile')
def compare_score_to_others():
    pass



   
  


# get_country_infobox('kenya')
# get_country_infobox('nigeria')
# get_country_infobox('canada')
# get_country_infobox('england')















##############################################################################
#Helper Functions

if __name__ == "__main__":
    app.run(debug=True)
    pass
    



