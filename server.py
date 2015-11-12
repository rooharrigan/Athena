
"""This is the server file for the Athena Wikipedia Quiz game. Running this file without
making changes will run the server for this game with the debugger on."""

##############################################################################
#Externals
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
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
#Define the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = 0
login_manager.login_view = "/"

@login_manager.user_loader
def user_loader(userid):
    return User.query.filter(User.id == userid).first()


#App Routes
@app.route('/signup', methods=(["POST"]))
def signup():
    """Process the signup form, check if the user already exists, and if not create them."""
    print "we're in the signup action"
    signup_form = SignupForm(request.form)

    if signup_form.validate_on_submit():
        password = str(signup_form.password.data)
        user = User(email=signup_form.signup_email.data, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect("/home")
    else:
        print "not valid on submission"
        return redirect("/")

#Ajax call from index.html, return Fail and write an if statement in JS to show an error.


@app.route('/login', methods=(["POST"]))
def login():
    """Process the login form.  Check that password and username are right and store user in session"""
    print "\n IN LOGIN ROUTE"
    login_form = LoginForm(request.form)
    print login_form
    print login_form.validate_on_submit()
    if login_form.validate_on_submit():
        print "\n \n IN FORM VALIDATE"
        password = str(login_form.password.data)
        user = User.query.filter(User.email == login_form.login_email.data).first()
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
            return redirect("/")
    return redirect("/")        


@app.route('/logout', methods=(["GET", "POST"]))
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    """Landing page with Santorini.  Login modal window is here."""
    print "we're in the login-signup form"
    signup_form = SignupForm()
    login_form = LoginForm()

    return render_template("index.html", signup_form=signup_form, login_form=login_form)


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
    
    wrong1, wrong2, wrong3 = make_wrong_capitals(country_name)   #failing at make wrong answers
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
    print "\n Country name: "
    print country_name
    right_answer = get_country_capital(country_name)
    print "\n right answer: "
    print right_answer
    #Grade the quiz
    if guess == right_answer:
        print "That's correct!"
        score = 100
    else:
        print "That's incorrect!"
        score = 0

    #Grab components of the quizevent and store it in the database
    user_id = current_user.id
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    country_id = country_obj.id
    continent_name = country_obj.continent_name

    quizevent = Quizevent(user_id=user_id, country_id=country_id, continent_name=continent_name, score=score)
    db.session.add(quizevent)
    db.session.commit()

    #Return the quiz score to the client
    nicety = (sample(compliments, 1))[0]
    return render_template ("quiz_score.html", score=score, nicety=nicety)


@app.route('/small_data')
def get_user_scores():
    """Show a graph of how users are doing on quizzes."""
    
    #Get current_user-level data
    user_id = current_user.id

    user_scores = {}

    continents = get_continents()
    for continent in continents:
        title = continent + " Scores"
        number_quizzes = Quizevent.query.filter(Quizevent.user_id == user_id, 
            Quizevent.continent_name == continent).count()
        sum_score = 0
        quiz_scores_tuple = (db.session.query(Quizevent.score).filter
            (Quizevent.user_id == user_id, Quizevent.continent_name == continent)
            .all())
        for i in quiz_scores_tuple:
            score = i.score
            sum_score += score
        if sum_score != 0:
            avg_score = sum_score / number_quizzes
            print "Your average score for {} quizzes is {}".format(continent, avg_score)
        else:
            print "\n You haven't taken any quizzes about {} yet!".format(continent)
            avg_score = None
        user_scores[continent] = avg_score

    print "\n \n Your scores: "
    for continent, score in user_scores.iteritems():
        print continent, score

    all_scores = get_all_scores()

    return render_template("small_data.html", user_scores=user_scores, all_scores=all_scores)


##############################################################################
#Static Functions

def get_all_scores():
    all_scores = {}
    continents = get_continents()
    for continent in continents:
        title = continent + "Scores"
        number_quizzes = (Quizevent.query.filter(Quizevent.continent_name ==
         continent).count())

        sum_score = 0
        quiz_scores_tuple = (db.session.query(Quizevent.score).filter
            (Quizevent.continent_name == continent).all())
        for i in quiz_scores_tuple:
            score = i.score
            sum_score += score
        if sum_score != 0:
            avg_score = sum_score/ number_quizzes
            print "The average score for {} quizzes is {}".format(continent, avg_score)
        else:
            print "\n No one has taken any quizzes about {} yet.".format(continent)
            avg_score = None
        all_scores[continent] = avg_score

    for continent, score in all_scores.iteritems():
        print continent, score

    return all_scores



def make_wrong_capitals(country_name):
    """Generates wrong answers for the capital quiz question. Returns as a set."""
    wrong_answers = set()

    #Make the right answer's country object
    country_object = Country.query.filter(Country.country_name == country_name).first()

    #Make country objects for wrong answers from same continent
    continent = country_object.continent_name
    list_of_country_objects = Country.query.filter(Country.continent_name == continent, Country.country_name != country_name).all()
    index_of_countries = len(list_of_country_objects) - 1

    wrong_index = randint(0, index_of_countries)
    while len(wrong_answers) < 3:
        if (list_of_country_objects[wrong_index]).capital in wrong_answers:
            wrong_index = randint(0, index_of_countries)
        else:
            country_object = list_of_country_objects[wrong_index]
            wrong_answers.add(country_object.capital)
        print "\n \n  answers"
    print wrong_answers
    return wrong_answers


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


def get_continents():
    continents = set()
    continent_list = Continent.query.filter(Continent.name != "Antarctica").all()
    for i in continent_list:
            continent = i.name
            continents.add(continent)
    return continents


##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app)

    # #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(debug=True)
    



