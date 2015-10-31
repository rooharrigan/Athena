
"""This is the server file for the Athena Wikipedia Quiz game. Running this file without
making changes will run the server for this game with the debugger on."""

##############################################################################
#Externals
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, current_user
from flask_debugtoolbar import DebugToolbarExtension
from pprint import pprint
from string import translate, lower
from random import randint, sample

#Internals
from model import connect_to_db, db, Country, User, Quizevent
from compliments import compliments

app = Flask(__name__)
app.secret_key = "Get up, get up, get up, get up, it's the first of the month."
##############################################################################
#App Routes


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


@app.route('/login_check', methods=['POST'])
def login_check():
    # check that a username and password were entered on form
    email = request.form.get("email")
    print "email: ", email
    password = request.form.get("password")
    print "password ", password

    # check database for user with username
    user = User.query.filter(User.email == email).first()
    print user
    if user:
        print "got user"
        # TODO: check password
        if True:
            login_user(user)
            print session
        else:
            print "bad password"

    else:
        print "bad user"


    # if email:
    #     login_user(user)
    #     print session

    return  redirect("/")


# check that a username and password were entered on form
# check database for user with username
#     if user
#         check password
#             if password matches user.password
#                 login(user)
#             else
#                 flash error
#     else
#         flash error







@app.route('/logout')
@login_required
def logout():
    #Even listener on the logout button
    #Hide logout button and show login button
    logout_user()
    return redirect("/")


@app.route('/')
def get_quiz_questions():
    """Handles login and returns the homepage"""
    if current_user:
        print "logged in as"
        print current_user
        # print 'Logged in as {}'.format(escape(session['email']))
    else:
        print "User is not logged in"

    return render_template("quiz_country.html")


@app.route('/quiz')
def generate_quiz():
    """Makes the capital quiz question. Queries database for the right answer,
    users make_wrong_answers for the other three."""
    #Get the country, right capital and three wrong capitals from the database
    country_name = (request.args.get("country")).title()
    capital = get_country_capital(country_name)
    
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
    guess = request.form.get("button")
    country_name = request.form.get("country_name")
    right_answer = get_country_capital(country_name)

    if guess == right_answer:
        print "That's correct!"
        score = 100
    else:
        print "That's incorrect!"
        score = 0


    nicety = (sample(compliments, 1))[0]
    return render_template ("quiz_score.html", score=score, nicety=nicety)

@app.route('/scores_data')
@login_required
def settings(): 
    pass


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


def get_country_capital(country_name):
    """Given a country name string, returns the country's capital or error message."""
    tup = db.session.query(Country.capital).filter(Country.country_name == country_name).first()
    capital = tup.capital
    if capital:
        print capital
        return capital
    else:
        print "Couldn't find the capital of" + country_name


##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app)

    #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(debug=True)
    



