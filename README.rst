============================
Athena
============================

**Athena** is a web application that creates geo-quizzes with interactive maps. You can focus on learning about a specific continent and compare scores with others in the Athena community.  Athena supports a secure login with password encryption, so you can safetly sign up with a phone number to receive capital quiz questions via text message. Optimized for mobile, you can check in on your Athena scores from anywhere and request another quiz text.

You can learn more about the developer on `LinkedIn <https://www.linkedin.com/in/rooharrigan>`_.

============================
  Contents
============================
- Technologies
- Current Features
- Future Features
- Data Wrangling
- Screenshots

============================
  Technologies
============================
Athena is built on a Flask server (written in Python) and uses a postgreSQL database.  The maps are built with the Google Maps API and the interactive polygon layers on top are done using Google Fusion Tables, KML files (some of which were homemade) and associated JavaScript, jQuery, and Ajax. The text messaging feature was built using the Twilio SMS API and tested using ngrok. The score displays were made using Chart.js. The HTML/CSS was put together using Bootstrap; some pieces are borrowed from the open-source theme `Grayscale <https://startbootstrap.com/template-overviews/grayscale/>`_.

Pythonic goodies:
- Brcypt: for password encryption
- WTForms and Flask-WTF:for making and validating forms on the server-side
- Flask-Login: for the login session and CSRF tokens
- Jinja: for templating, and other trickery
- SQLAlchemy and Flask-SQLAlchemy: for talking with postgres

============================
  Current Features
============================
- The landing page shows a quick bio of the app and some more ways to reach the creator, plus login and signup form in a modal window. The form does some front-end username checking (for uniqueness, using an Ajax query) and password checking (for length greater than 5 and use of a number).  There's also an easter egg in there for anyone who loves apples. After the user submits the form, the server does the same type of user/password checking on the backend.

- The homepage map uses a polygon layer of the continents to display basic InfoWindows™ and navigate you to a quiz about a randomized country on the selected continent. 

- The quiz displays four questions about the country of choice, including an interactive map upon which you must locate the country. Wrong answers are always concocted from the right answers for neighboring countries.

- The small data page queries the database to show your scores compared to the rest of the Athena user community using polar area charts.

- The daily quiz page allows you to sign up for quiz questions using your phone number and request a new question to your phone with the click of a button.  It also displays a polar area chart showing your scores for all capitals.
  The dail quiz text appears to the user in this form:

        What is the capital of Egypt?
          A.Cairo
          
          B.Nairobi
          
          C.Ouagadougou
          
          D.Addis Ababa

  Users can text back either the letter or the full name of the capital city in response. They will receive their score via    text and can see an updated chart of all their scores back on the daily quiz page. 
  Users can only work on one daily quiz question at a time, and can only text in one quiz response.

============================
  Future Features
============================
- Set up Twilio API call to run once daily on all phone numbers in the database to send a daily quiz question; investigate date/time library for timing the question.

- Improve form checking for the quiz; force user to fill out all four questions before submit button is available

- Create custom map style on Googlemaps API

- Fix background of base body to be prettier, stylize the Jumbotron score, consider animating the score

- Fix the center circle to have downscroll animation on the landing page

- Revamp demonym quiz question for certain countries to be trickier

- Create a continent-specific geoquiz where user has to locate all countries on the continent

- Time the quiz

============================
  Data Wrangling
============================
The database for most of Athena's textual information was initially seeded using a query to the Mediawiki API and careful parsing of the jsonified Infobox that we all know and love from the right-hand side of every Wikipedia page ever.  After significant experimentation and unicode issues, I switched to using the `RESTCountries API <https://restcountries.eu/>`_
Athena uses two Google Fusion Tables of KML data to create the polygon layers you see on the maps.  The country polygons were taken from the `World Country Boundaries <https://www.google.com/fusiontables/DataSource?docid=1MxmNwQ67Doekao1xTAV9vyNEOoX0lKf8z_B3bJez>`_ table.  To my great surprise, the internet held no reasonable-looking KML data in KML or SHP form to delineate each continent, so I created those rough polygons myself in Google Maps and exported them.
The data model for Athena is relatively straightforward: 5 tables hold user, country, continent, quizevent, and capquiz information respectively.  The capquizzes table has a unique user id constraint, so a user can only be working on a single quiz question at a time. 

============================
  Screen shots
============================
Coming soon!
