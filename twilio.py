##############################################################################
#Externals
from flask import Flask, request, render_template, session, redirect, url_for, escape, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

#Twilio tools 
from twilio.rest import TwilioRestClient
from secrets import account_sid, auth_token

account_sid = account_sid
auth_token = auth_token
client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(
    to="+17329393694", 
    from="+14152149799",
    body="Twilio. More like Roolio.")