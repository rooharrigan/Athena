============================
Athena
============================

**Athena** is a web application that creates geo-quizzes with interactive maps. Users can focus on learning about a specific continent and compare scores with others in the Athena community.  Athena supports a secure login with password encryption, so users can safetly sign up with thier phone numbers to receive capital quiz questions via text message. Optimized for mobile, Athena users can check in on their scores from anywhere and request a quiz text.

You can learn more about the developer on `LinkedIn <https://www.linkedin.com/in/rooharrigan>`.

============================
  Contents
============================
- Technologies
- Features
- Data Wrangling
- APIs
- Data Structure
- Screenshots

============================
  Technologies
============================
Athena is built on a Flask server (written in Python) and uses SQL Alchemy to talk with its postgreSQL database.  The maps are built with the Google Maps API and the interactive polygon layers on top are done using Google Fusion Tables, KML files (some of which were homemade) and associated JavaScript and jQuery. The text messaging feature is built using the Twilio SMS API.
Back-to-Front: postgreSQL, Python, Flask, Jinja, JavaScript, jQuery, Ajax, Bootstrap

============================
  Features
============================
Current Features
*The landing page shows a quick bio of the app and some more ways to reach the creator, plus login and signup form in a modal window. The form performs some front-end username checking (for uniqueness) and password checking (for length greater than 5 and use of a number). There's also an easter egg in there for anyone who loves apples.

Future Plans
