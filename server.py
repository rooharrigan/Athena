
"""This is the server file for the Athena Wikipedia Quiz game. Running this file without
making changes will run the server for this game with the debugger on."""

##############################################################################
#App Routes

from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask_debugtoolbar import DebugToolbarExtension
from pprint import pprint
from string import translate, lower
from random import randint, sample

from model import connect_to_db, db, Country, User, Quizevent



app = Flask(__name__)
app.secret_key = "Get up, get up, get up, get up, it's the first of the month."

     

##############################################################################
#App Routes

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


@app.route('/')
def get_quiz_questions():
    """Handles login and returns the homepage"""
    if 'username' in session:
        print 'Logged in as {}'.format(escape(session['username']))
    else:
        print "User is not logged in"

    return render_template("quiz_country.html")


@app.route('/quiz')
def generate_quiz():
    """Makes the capital quiz question. Queries database for the right answer,
    users make_wrong_answers for the other three."""
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
        answer4=answer4,
        )


@app.route('/quiz_score', methods=['POST'])
def grade_quiz():
    """Grade the quiz and update the database with a quizevent"""
    #It's the name that matters
    print "we're in the quiz_score route!"
    print "##############################"
    guess = request.form.get("site")
    print type(guess)
    print guess



    # guess2 = request.form.get("button2")
    # guess3 = request.form.get("button3")
    # guess4 = request.form.get("button4")




    # user_score = '0%'

    # if request.form.get("quiz-score") == capital:
    #     user_score = '100%'
    # else:
    #     user_score = '0%'


    # nicety = "Great work!"
    # score = user_score
    # return render_template (quiz_score, score=score, nicety=nicety)



# @app.route('/name', methods=['POST'])

# button clicked = requiest.form.get()
# return 


##############################################################################
#Static Functions



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


def add_quizevent(country_name):
    if session['username']:
        email = session['username']
        user_id = db.session.query(User.id).filter(email == email).first()
    else:
        user_id = 1

    country_id_tuple = db.session.query(Country.id).filter(Country.country_name == country_name).first()
    country_id = country_id_tuple[0]
    print country_id

    new_quiz = Quizevent(user_id=user_id, country_id=country_id)
    print new_quiz



##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app)

    #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(debug=True)
    



