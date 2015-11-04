"""All postable forms for Athena"""

##############################################################################
#Externals
from flask import Flask, redirect, render_template
from flask_wtf import Form
from wtforms import BooleanField, TextField, validators, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError
from itsdangerous import URLSafeTimedSerializer

#Internals
from model import connect_to_db, db, User

##############################################################################
#Functions

#Validator: checks signup emails against existing users in database
class Unique(object):                       
    def __init__(self, model, field, message=u'This guy already exists.'):
        self.model = model              #the User model, usually
        self.field = field              #the email field
        self.message = message


    def __call__(self, form, field):
        #Example query: User.query.filter(User.email == email_from_form).first()
        check = self.model.query.filter(self.field == field.data).first()   # .exists()
        if check:                                     #If you find the email in the database
            raise ValidationError(self.message)         #raise a validation error using the message definied in __init__


#Email/password signup form
class LoginForm(Form):
    email = TextField('Email', validators=[
        InputRequired(), 
        Email()])
    password = PasswordField('Password', validators=[
        InputRequired()])


class SignupForm(LoginForm):
    email = TextField('Email', validators=[
        InputRequired(), 
        Email(), 
        Unique(User, User.email, message="You've already got an account. Login.")
        ])


