
"""This is the server file for the Athena Wikipedia Quiz game. Running this file without
making changes will run the server for this game with the debugger on."""

##############################################################################
#Externals
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask_debugtoolbar import DebugToolbarExtension
#Login Checks and Forms
from flask_wtf import Form
from wtforms import BooleanField, TextField, validators, PasswordField
from itsdangerous import URLSafeTimedSerializer
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
#Python Libraries
from pprint import pprint
from string import translate, lower
from random import randint, sample

#Internals
from model import connect_to_db, db, User, Continent, Country, Quizevent
from forms import SignupForm, LoginForm
from compliments import compliments


app = Flask(__name__)
app.secret_key = "Get up, get up, get up, get up, it's the first of the month."
##############################################################################
#Defin the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = None
login_manager.login_view = "/"
@login_manager.user_loader
def user_loader(userid):
    return User.query.filter(User.id == userid).first()


#App Routes
@app.route('/login-signup-form', methods=(["GET"]))
def show_form():
    print "we're in the login-signup form"
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template("login.html", signup_form=signup_form, login_form=login_form)


@app.route('/signup', methods=(["POST"]))
def signup():
    """Process the signup form, check if the user already exists, and if not create them."""
    print "we're in the signup action"
    form = SignupForm(request.form)
    if form.validate_on_submit():
        password = str(form.password.data)
        user = User(email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect("/home")
    else:
        flash("Please enter a valid email.")
        print "not valid on submission"
        return redirect("/login-signup-form")


@app.route('/login', methods=(["POST"]))
def login():
    """Process the login form.  Check that password and username are right and store user in session"""
    form = LoginForm(request.form)
    if form.validate_on_submit():
        password = str(form.password.data)
        user = User.query.filter(User.email == form.email.data).first()
        if user:
            if user.check_password(password):
                print "\nValid user!"
                login_user(user, remember=True)
                return redirect('/home')
            else:
                print "Invalid password"
                flash("Username or password incorrect")
        else:
            print "\nInvalid email"
            flash("Username or password incorrect")
            return redirect("/login-signup-form")
    return redirect("/login-signup-form")        


@app.route('/logout', methods=(["GET", "POST"]))
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    """Landing page with Santorini.  Modal window should go here."""
    return render_template("index.html")


@app.route('/home')
@login_required
def choose_quizes():
    """Place to choose what you want to learn about"""

    return render_template("quiz_home.html")


@app.route('/cap-quiz')
def get_quiz_questions():
    """Choose country you want to learn about."""

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
    #Grade the quiz
    if guess == right_answer:
        print "That's correct!"
        score = 100
    else:
        print "That's incorrect!"
        score = 0

    user_id = current_user.id
    print "User Id: "
    print type(user_id)
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    country_id = country_obj.id
    print "country id: "
    print country_id
    print type(country_id)

    quizevent = Quizevent(user_id=user_id, country_id=country_id, score=score)
    db.session.add(quizevent)
    db.session.commit()

    nicety = (sample(compliments, 1))[0]
    return render_template ("quiz_score.html", score=score, nicety=nicety)


@app.route('/small_data')
def show_small_data():
    """Show a graph of how users are doing on quizzes"""
    print "You're in small data!"
    
    return render_template("small_data.html")


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
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    capital = country_obj.capital
    if capital:
        print capital
        return capital
    else:
        print "Couldn't find the capital of" + country_name


##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app)

    # #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(debug=True)
    



