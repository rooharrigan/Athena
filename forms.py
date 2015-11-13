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
    email = TextField('Email', id="login-email", validators=[
        InputRequired(), 
        Email()])
    password = PasswordField('Password', id="login-password", validators=[
        InputRequired()])


class SignupForm(Form):
    email = TextField('Email', id="signup-email", validators=[
        InputRequired(), 
        Email(), 
        Unique(User, User.email, message="You've already got an account. Login.")
        ])
    password = PasswordField('Password', id="signup-password", validators=[
        InputRequired()])


#Super uncool. I wanted to set Signfup form to inherit from LoginForm and only
#use the Unique method as the one difference. However, when these forms get
#created in the DOM, they get THE SAME HTML ID (because the id is created by
#by wtforms for you. WTF. That's useless because it confuses Ajax completely). And
#I couldn't think of a way to have the id parameter dynamically udpate based on
#the variable name of the form being instatiated. So eff it. I made two forms. ;()




