
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask_debugtoolbar import DebugToolbarExtension
from pprint import pprint
from string import translate, lower
from random import randint, sample

from model import connect_to_db, db, Country, User



app = Flask(__name__)
app.secret_key = "Get up, get up, get up, it's the first of the month."

#Imports and flask app call

##############################################################################
#Static Functions


     

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
    """Makes the capital quiz question by querying the database 
    for the right answer and using make_wrong_answers for the others."""
    #Get the country, right capital and three wrong capitals from the database
    country_name = request.args.get("country")
    country_name = country_name.title()
    tup = db.session.query(Country.capital).filter(Country.country_name == country_name).first()
    capital = tup.capital
    wrong1, wrong2, wrong3 = make_wrong_answers(country_name)
    answers = (capital, wrong1, wrong2, wrong3)

    #Randomize into four answers and pass to the user
    answer1, answer2, answer3, answer4 = sample(answers, 4)

    return render_template('quiz_questions.html', 
        country_name=country_name, 
        answer1=answer1, 
        answer2=answer2,
        answer3=answer3,
        answer4=answer4)

 
def make_wrong_answers(country_name):
    """Generates wrong answers for the capital quiz question"""
    #Count the number of countries in table
    number_of_countries = Country.query.count()     #192 seeded as of October 30, 2015
    answer_ids = []
    answers = []

    #Get the right answer's id
    country_object = db.session.query(Country.id).filter(Country.country_name == country_name).first()
    right_id = country_object.id
    answer_ids.append(right_id)

    #Pick random id's and make wrong answer ids
    wrong_id = randint(1, number_of_countries)
    while len(answer_ids) < 4:
        if wrong_id in answer_ids:
            wrong_id = randint(1, number_of_countries)
        else:
            answer_ids.append(wrong_id)
    else: 
        answer_ids = answer_ids[1:]
        for i in answer_ids:
            country_object = db.session.query(Country.capital).filter(Country.id == i).first()
            answer = country_object.capital
            answers.append(answer)
        return answers


@app.route('/quiz_score')
def grade_quiz():
    nicey = "Great work!"
    score = 100
    return render_template (quiz_score, score=score, nicety=nicety)


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
    



