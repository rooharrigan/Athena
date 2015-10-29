
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask_debugtoolbar import DebugToolbarExtension
from pprint import pprint
from string import translate, lower

from model import connect_to_db, db, Country, User



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
def generate_quiz():
    country_name = request.args.get("country")
    country_name = country_name.title()

    capital = db.session.query(Country.capital).filter(Country.country_name == country_name).all()

    # wrong1, wrong2, wrong3 = 
    # , wrong1=wrong1, wrong2=wrong2, wrong3=wrong3

    return render_template('quiz_questions.html', country_name=country_name, capital=capital)


@app.route('/quiz_score')
def grade_quiz():
    pass


@app.route('/percentile')
def compare_score_to_others():
    pass

 


##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app)

    #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(debug=True)
    



