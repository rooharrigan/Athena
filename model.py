##############################################################################
#Externals
from flask import Flask, Response
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, confirm_login
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# This is the connection to the postgreSQL database; we get it from the 
# Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Model definitions

class Country(db.Model):
    """Stores countries and their attributes, seeded from Wikipedia"""

    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_name = db.Column(db.String, nullable=False)
    capital = db.Column(db.String, nullable=True)

    def __repr__(self):
        return "<Country country_name=%s>" % (self.name)


class User(db.Model, UserMixin):
    """Stores user id and email information."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)           #previously using db.String, hashed as numbers
    avg_score = db.Column(db.Integer, nullable=True)
    quizzes_taken = db.Column(db.Integer, nullable=True)
    #Inheriting from UserMixin gives you defaults of is_authenticated(), is_active(), is_anonymous(), and get_id() functions required by Flask-Login

    def __init__(self, email, password):
        print "I am initting"
        self.email = email
        self.set_password(password)


    def __repr__(self):
        return "<User email=%s>" % (self.email)


    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())      #salts and hashes a password. Salt is randomly generated by bcrypt
        print "The password set on this user is: "
        print self.password_hash


    def check_password(self, password): ##AARON
        encoded_pw = self.password_hash.encode('utf-8')
        return bcrypt.hashpw(password, encoded_pw) == encoded_pw


    def add_quiz_taken(self):
        """TODO"""
        self.quizzes_taken += 1


    def update_average(self, new_score):
        """Updates the user's overall average score."""
        new_avg = (self.avg_score * (self.quizzes_taken - 1) + new_score)/(self.quizzes_taken)
        self.avg_score = new_avg



class Quizevent(db.Model):
    """Stores individual quiz event information."""

    __tablename__ = "quizevents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    score = db.Column(db.String, nullable=True)             #not sure how to get the quiz ID in there becase it happens in a separate route

    user = db.relationship('User', backref='quizzes')
    country = db.relationship('Country', backref='quizzes')

    def __repr__(self):
        return "<Quizevent id=%d country_id=%s>" % (self.id, self.country_id)




##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use posgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/Athena'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()

