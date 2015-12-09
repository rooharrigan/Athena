
"""This is the server file for the Athena Wikipedia Quiz game. Running this file without
making changes will run the server for this game with the debugger on."""

##############################################################################
#Flask
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash, jsonify
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
import os
#Internals
from model import connect_to_db, db, User, Continent, Country, Quizevent, Capquiz
from forms import SignupForm, LoginForm
from compliments import compliments
#Twilio
from twilio.rest import TwilioRestClient
import twilio.twiml


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "Wake up, get up, get up, get up, it's the first of the month.")
##############################################################################
#Login/Signup Settings
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
        user = User(email=signup_form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect("/home")
    else:
        print "not valid on submission"
        return redirect("/")

# TODO: Ajax call from index.html, return Fail and write an if statement in JS to show an error.
# @app.route('/check_email', methods=["POST"])
# def check_unique_email():
#     """Handles Ajax call from signup form to check whether email entered is already in the database."""
#     email = request.form.get("signup-email")        #is it ID or Name of element?
#     if User.query.filter(User.email == email).first():
#         print "That email already has an account."
#         response = "That email already has an account."
#     else:
#         print "Unique user! Go ahead."
#         response = "Email passes all requirements."

#     return response


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
        user = User.query.filter(User.email == login_form.email.data).first()
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


##############################################################################
#Quiz Routes

@app.route('/home')
@login_required 
def choose_quizes():
    """Place to choose what you want to learn about"""

    return render_template("quiz_home.html")


@app.route('/country', methods=['POST'])
def get_country_questions():
    """Choose country you want to learn about."""

    return render_template("quiz_country.html")


@app.route('/continent', methods=['GET', 'POST'])
def get_continent():
    """Takes in continent from quiz_home.html page, finds a country, and sends the
    country name to the success function of the Ajax call that creates the country quiz."""
    print "We hit the continent route"
    continent = request.args.get("continent")
    print continent
    country_list = db.session.query(Country).filter(Country.continent_name == continent).all()
    country = sample(country_list, 1)[0]
    country = country.country_name
    print country
    return country


@app.route('/country_quiz/<country_name>')
def generate_quiz(country_name):
    """Makes the country-level quiz questions. Queries database for the right answer,
    users make_wrong_answers for the other three."""

    #Get the country and all the right answers
    country_name = country_name
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    capital, demonym, primary_langs = get_right_answers(country_obj)
    continent = country_obj.continent_name

    print primary_langs
    print type(primary_langs)

    #Make the wrong answers
    wrongcap1, wrongcap2, wrongcap3 = make_wrong_capitals(country_obj)
    cap_answers = (capital, wrongcap1, wrongcap2, wrongcap3)

    wrong_dems = make_wrong_demonyms(country_name, demonym)
    wrongdem1, wrongdem2, wrongdem3 = wrong_dems[:3]
    dem_answers = (demonym, wrongdem1, wrongdem2, wrongdem3)
    lang_answers = make_langs(country_name)

    #Randomize into four answers and pass to the user
    cap1, cap2, cap3, cap4 = sample(cap_answers, 4)
    dem1, dem2, dem3, dem4 = sample(dem_answers, 4)
    lang1, lang2, lang3, lang4 = sample(lang_answers, 4)

    return render_template('quiz_questions.html', 
        country_name=country_name, 
        continent=continent,
        cap1=cap1, 
        cap2=cap2,
        cap3=cap3,
        cap4=cap4,
        dem1=dem1,
        dem2=dem2,
        dem3=dem3,
        dem4=dem4,
        lang1=lang1,
        lang2=lang2,
        lang3=lang3,
        lang4=lang4
        )


@app.route('/quiz_score', methods=['POST'])
def grade_quiz():
    """Grade the quiz and update the database with a quizevent"""
    #Get right answers
    country_name = request.form.get("country_name")
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    capital, demonym, primary_langs = get_right_answers(country_obj)

    #Get guesses
    cap_guess = request.form.get("cap-button")
    dem_guess = request.form.get("dem-button")
    lang_guess = request.form.get("lang-button")
    print "\n\n\n\n\n  LANGUAGE GUESS"
    print lang_guess

    print "Right Answer: "
    print primary_langs

    geo_guess = request.form.get("map-guess")
    print "Guesses: "
    print cap_guess, dem_guess, lang_guess, geo_guess

    #Print right answers:
    print "\n Country name: "
    print country_name
    print "\n right answers: "
    print capital, demonym, primary_langs, country_name

    #Grade quiz
    score_num = 0
    score_denom = 4.0

    if cap_guess == capital:
        print "Right capital"
        score_num += 1.0
        print score_num
    if dem_guess == demonym:
        print "right demonym"
        score_num += 1.0
        print score_num
    if lang_guess == primary_langs:
        print "right langs"
        score_num += 1.0
        print score_num
    if geo_guess == country_name:
        print "right geo guess"
        score_num += 1.0
        print score_num


    #Calculate score
    score = int(100 * (score_num / score_denom))

    #Grab components of the quizevent and store it in the database
    user_id = current_user.id
    country_id = country_obj.id
    continent_name = country_obj.continent_name

    quizevent = Quizevent(user_id=user_id, country_id=country_id, continent_name=continent_name, score=score, quiz_type='full')
    db.session.add(quizevent)
    db.session.commit()

    #Return the quiz score to the client
    nicety = (sample(compliments, 1))[0]
    return render_template ("quiz_score.html", score=score, nicety=nicety)


@app.route('/small_data')
def show_small_data():
    """Show a graph of how users are doing on quizzes."""

    #Get Current User's scores
    user_scores = get_user_scores(current_user, 'full')
    print "\n \n Your scores: "
    for continent, score in user_scores.iteritems():
        print continent, score

    #Get Athena scores
    all_scores = get_all_scores()
    print "\n \n Athena scores: "
    print all_scores

    return render_template("small_data.html", user_scores=user_scores, all_scores=all_scores)


@app.route('/capquiz_data.json')
def make_capquiz_chart():
    """Creates user capitals scores data for chart.js display"""

    quiz_type = 'caps' 
    user_scores = get_user_scores(current_user, quiz_type)
    userData = {
        'continents': [{
            "value": user_scores["North America"],
            "color": "#ff1a1a",
            "highlight": "#66e0ff",
            "label": "North America"
        },
        {
            "value": user_scores["South America"],
            "color": "#ff704d",
            "highlight": "#66e0ff",
            "label": "South America"
        },
        {
            "value": user_scores["Africa"],
            "color": "#ffff33",
            "highlight": "#66e0ff",
            "label": "Africa"
        },
        {
            "value": user_scores["Europe"],
            "color": "#99ccff",
            "highlight": "#66e0ff",
            "label": "Europe"
        },
        {
            "value": user_scores["Asia"],
            "color": "#33adff",
            "highlight": "#66e0ff",
            "label": "Asia"
        },
        {
            "value": user_scores["Oceania"],
            "color": "#F7464A",
            "highlight": "#66e0ff",
            "label": "Oceania"
        }]
    }
    print "\n \n USERDATA###", userData

    return jsonify(userData)
 


@app.route('/user_data.json')
def make_user_chart():
    """Creates user scores data for chart.js display"""

    quiz_type = 'full'
    user_scores = get_user_scores(current_user, quiz_type)
    userData = {
        'continents': [{
            "value": user_scores["North America"],
            "color": "#ff1a1a",
            "highlight": "#66e0ff",
            "label": "North America"
        },
        {
            "value": user_scores["South America"],
            "color": "#ff704d",
            "highlight": "#66e0ff",
            "label": "South America"
        },
        {
            "value": user_scores["Africa"],
            "color": "#ffff33",
            "highlight": "#66e0ff",
            "label": "Africa"
        },
        {
            "value": user_scores["Europe"],
            "color": "#99ccff",
            "highlight": "#66e0ff",
            "label": "Europe"
        },
        {
            "value": user_scores["Asia"],
            "color": "#33adff",
            "highlight": "#66e0ff",
            "label": "Asia"
        },
        {
            "value": user_scores["Oceania"],
            "color": "#F7464A",
            "highlight": "#66e0ff",
            "label": "Oceania"
        }]
    }
    print "\n \n USERDATA###", userData

    return jsonify(userData)
 

@app.route('/athena_data.json')
def make_athena_chart():
    """Creates athena scores data for chart.js display"""

    all_scores = get_all_scores()

    athenaData = {
        'continents': [{
            "value": all_scores["North America"],
            "color": "#ff1a1a",
            "highlight": "#66e0ff",
            "label": "North America"
        },
        {
            "value": all_scores["South America"],
            "color": "#ff704d",
            "highlight": "#66e0ff",
            "label": "South America"
        },
        {
            "value": all_scores["Africa"],
            "color": "#ffff33",
            "highlight": "#66e0ff",
            "label": "Africa"
        },
        {
            "value": all_scores["Europe"],
            "color": "#99ccff",
            "highlight": "#66e0ff",
            "label": "Europe"
        },
        {
            "value": all_scores["Asia"],
            "color": "#33adff",
            "highlight": "#66e0ff",
            "label": "Asia"
        },
        {
            "value": all_scores["Oceania"],
            "color": "#F7464A",
            "highlight": "#66e0ff",
            "label": "Oceania"
        }]
    }

    return jsonify(athenaData)
 

@app.route('/dailycapquiz')
def twilio_form():
    """Shows the Twilio phone signup. If signed up, shows a chart of scores and
    opportunity to get a new score."""
    #Get Current User's scores
    user_scores = get_user_scores(current_user, 'caps')
    print "\n \n Your scores: "
    for continent, score in user_scores.iteritems():
        print continent, score

    return render_template("twilio_signup.html", user_scores=user_scores)


@app.route('/dailycapquiz_question', methods=['POST'])
def t():
    """If the user is a first-time signup: validates user phone number, stores
    in datbase, sends text confirmation, and sends first quiz question.
    If the user is already signed up: sends a new quiz question.
    Both forms in twilio_signup.html submit POST requests to this route."""
    client = TwilioRestClient()
    twilio_number = os.environ.get("TWILIO_NUMBER")

    #For the deployed app, disable this function and reroute to error page
    if PORT != 5000:
        return render_template("under_construction.html")

    print "We continued past the PORT!=5000 line."
    # Store new number in database and send signup confirmation message
    if current_user.phone_number == None:
        number = request.form.get("phone-number")
        current_user.phone_number = number
        number = "+1" + number                  ##TODO remove when +1 is fixed
        print number
        db.session.commit()

        message_welcome = client.messages.create(to=number, 
                from_=twilio_number,
                body="Ahoy! Thanks for signing up for my capitals quiz.")

    #For the local app, make quiz
    else:
        index = randint(21, 60)
        if index == 28:
            index = 29
        country_obj = Country.query.filter(Country.id == index).first()
        country = country_obj.country_name
        print "\n\n" "name: " + country
        country_id = country_obj.id
        continent = country_obj.continent_name
        cap_answers = make_cap_question(country_obj)
        cap1, cap2, cap3, cap4 = sample(cap_answers, 4)
        cap1 = cap1.decode('ascii', 'ignore')
        cap2 = cap2.decode('ascii', 'ignore')
        cap3 = cap3.decode('ascii', 'ignore')
        cap4 = cap4.decode('ascii', 'ignore')
        print "\n" + cap1, cap2, cap3, cap4

        message_string = """
            What is the capital of {}?
            A: {}
            B: {}
            C: {}
            D: {}
            """.format(country, cap1, cap2, cap3, cap4)
        print message_string

        # Send Quiz Question
        number = current_user.phone_number
        number = "+1" + number                      #TODO REmove this when +! number is fixed
        message_quiz = client.messages.create(to=number, 
                from_=twilio_number,
                body=message_string)

        #Create currentcapQuiz event
        user_id = current_user.id
        capquiz = Capquiz(user_id=user_id, country_id=country_id, A=cap1, B=cap2, C=cap3, D=cap4)
        db.session.add(capquiz)
        db.session.commit()

    return redirect("/dailycapquiz")


@app.route("/twilio_response", methods=['GET', 'POST'])
def twilio_response():
    """Grades the quiz, stores the score in the database in Quizevents table,
    and tells user their score."""

    #Who texted Athena?
    user_number = request.values.get('From', None)
    user_number = user_number[2:]   #TODO remove this when the +1 fixed
    user_obj = User.query.filter(User.phone_number == user_number).first()
    print "\n User ID"
    user_id = user_obj.id

    #Get their current capquiz object
    capquiz_obj = Capquiz.query.filter(Capquiz.user_id == user_id).first()
    if capquiz_obj == None:
        message_string = "Sorry, you only get one guess. Enjoy tomorrow's quiz!"
    else:
        country_id = capquiz_obj.country_id
        country_obj = Country.query.filter(Country.id == country_id).first()
        continent_name = country_obj.continent_name

        #Compare user guess to the right answer
        guess = request.values.get('Body', None)
        print "\n \n \n  WHAT ROO TEXTED BACK: "
        print guess

        if guess == 'A':
            guess = capquiz_obj.A
        if guess == 'B':
            guess = capquiz_obj.B
        if guess == 'C':
            guess = capquiz_obj.C
        if guess == 'D':
            guess = capquiz_obj.D

        capital = country_obj.capital
        print "This is your guess: "
        print guess
        print "this is the right answer: "
        print capital

        if guess == capital:
            print "SCORE IS 100!"
            score = 100
        else:
            print "SCORE IS 0"
            score = 0

        quiz_type = 'caps'

        #Add to the overall Quizevents table
        quizevent = Quizevent(user_id=user_id, country_id=country_id, continent_name=continent_name, score=score, quiz_type=quiz_type)
        db.session.add(quizevent)

        #Clear out capquiz row for current_user_id before response
        db.session.delete(capquiz_obj)
        db.session.commit()

        #Text message score back to user
        if score == 0:
            message_string = "Incorrect. Study hard!"
        if score == 100:
            message_string = "That's correct! You are so smart."

    resp = twilio.twiml.Response()
    resp.message(message_string)
    return str(resp)    


##############################################################################
#Static Functions

def make_cap_question(country_obj):
    #Get the country and all the right answers
    capital = country_obj.capital

    #Make answers
    wrongcap1, wrongcap2, wrongcap3 = make_wrong_capitals(country_obj)
    cap_answers = (capital, wrongcap1, wrongcap2, wrongcap3)

    return cap_answers


def get_user_scores(current_user, quiz_type):
    """Gets all scores per quiz type for current user, feeds 'full' quiz chart in 
    Small Data route and 'caps' quiz chart in Daily Quiz route.
    Returns a dictionary."""
    user_id = current_user.id
    user_scores = {}
    continents = get_continents()
    for continent in continents:
        title = continent + " Scores"
        number_quizzes = Quizevent.query.filter(Quizevent.user_id == user_id, 
            Quizevent.continent_name == continent, Quizevent.quiz_type == quiz_type).count()
        sum_score = 0
        quiz_scores_tuple = (db.session.query(Quizevent.score).filter
            (Quizevent.user_id == user_id, Quizevent.continent_name == continent, Quizevent.quiz_type == quiz_type)
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
    return user_scores


def get_all_scores():
    """Gets 'full' quiz scores for the all users of Athena's World, feeds chart
    in Small Data route. Returns a dictionary."""
    all_scores = {}
    continents = get_continents()

    #For each continent
    for continent in continents:
        title = continent + "Scores"
        number_quizzes = (Quizevent.query.filter(Quizevent.continent_name ==
         continent).count())

        #Get sum of scores / number of scores, store in dictionary
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


def make_wrong_capitals(country_obj):
    """Generates wrong answers for the capital quiz question. Returns as a set."""
    wrong_answers = set()

    #Get country components from country object
    country_name = country_obj.country_name
    continent = country_obj.continent_name
    list_of_country_objects = Country.query.filter(Country.continent_name == continent, Country.country_name != country_name).all()
    index_of_countries = len(list_of_country_objects) - 1

    #Make a set with 3 unique wrong answers. Check against the right answer
    wrong_index = randint(0, index_of_countries)
    while len(wrong_answers) < 3:
        if (list_of_country_objects[wrong_index]).capital in wrong_answers:
            wrong_index = randint(0, index_of_countries)
        else:
            country_object = list_of_country_objects[wrong_index]
            wrong_answers.add(country_object.capital)
    print wrong_answers
    return wrong_answers


def make_langs(country_name):
    """Generates all four answers for the primary language quiz question, 
    including the right answer. Returns as a set."""
    langs = set()

    #Make country objects for wrong answers from same continent
    country_obj = Country.query.filter(Country.country_name == country_name).first()
    right_langs = country_obj.languages
    right_langs = str(right_langs)
    right_langs = translate(right_langs, None, '{"}')
    langs.add(right_langs)
    if country_obj.continent_name == "Caribbean":
        langs.add("English, Spanish")

    continent = country_obj.continent_name
    nearby_countries = Country.query.filter(Country.continent_name == continent, Country.country_name != country_name).all()
    top_index = len(nearby_countries) - 1
    print top_index

    while len(langs) < 4:
        index = randint(0, top_index)
        wrong_lang = (nearby_countries[index]).languages
        wrong_lang = str(wrong_lang)
        wrong_lang = translate(wrong_lang, None, '{"}')
        langs.add(wrong_lang)
        print langs
        print len(langs)


    return langs


def make_wrong_demonyms(country_name, demonym):
    """Generates 4 wrong answers for the demonym question, and compares against
    right demonym. Could return a list of 3 or 4 answers."""
    options = set()
    wrong_answers = []

    if country_name[-1] in ['a', 'e', 'i', 'o', 'y']:
        print "first if"
        options.add(country_name[:-1] + 'an')
        options.add(country_name[:-1] + 'ian')
        options.add(country_name[:-1] + 'i')
        options.add(country_name[:-1] + 'en')
    elif country_name[-1] == 'n':
        print "second if"
        options.add(country_name[:-1] + 'ian')
        options.add(country_name + 'i')
        options.add(country_name + 'ean')
        options.add(country_name + 'ese')
    else:
        print "else"
        options.add(country_name + 'an')
        options.add(country_name + 'si')
        options.add(country_name + 'sian')
        options.add(country_name + 'i')

    for i in options:
        if i != demonym:
            wrong_answers.append(i)

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


def get_right_answers(country_obj):
    """Given a country object, returns the country's right answers for the  quiz."""
    capital = country_obj.capital
    demonym = country_obj.demonym
    primary_langs = str(country_obj.languages)
    primary_langs = translate(primary_langs, None, '{"}')
    print type(primary_langs)

    if primary_langs:
        print capital, demonym, primary_langs
        answers = (capital, demonym, primary_langs)
        return answers
    else:
        print "Couldn't find all answers for" + country_name


def get_continents():
    """Grabs a list of all continents straight from the database."""
    continents = set()
    continent_list = Continent.query.filter(Continent.name != "Antarctica").all()
    for i in continent_list:
            continent = i.name
            continents.add(continent)
    return continents


##############################################################################
#Helper Functions

if __name__ == "__main__":    
    connect_to_db(app, os.environ.get("DATABASE_URL"))

    # #Use the DebugToolbar

    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)



