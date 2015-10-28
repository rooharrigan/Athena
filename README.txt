##Synopsis

##Motivation

##Athena Minimum Viable Product
============

Web application that scrapes a Wikipedia page about a country, generates a multiple-choice quiz question asking the country’s capital (with wrong answers being other capitals of other countries surrounding it) and stores the user’s response in a database for future data modeling.

MVP Core Functionality
*Login/Logout:
    Check login information against the database before adding it
    Store login information in the session

*Connect to MediaWiki (Wikipedia API)
    Scrape country’s capital out of country.
    Scrape the country’s location, look up countries surrounding it, and scrape their capitals
   
*Generate the quiz question with one wrong right answer and three wrong ones
    3 wrong answers must be based on the surrounding countries’ capitals

*Format the quiz question in a form and serve it up to the client

*Record the client’s response to the question and pass it back to the server. Store it in the database.

*Format a quiz score and serve it up to the client.

*Provide navigation between wikipedia and the quiz.



##Add-on Features (in no order):
============
*Randomly select questions so quizzes are different each time
*User login
*Logged in users can save scores
*Display scores using d3 graphs
*Compare to other users
*Allow users to add questions
*Geography questions asking users to identify things on a map
*Quiz as a Chrome plugin??

##API Reference

##Tests

##Contributors
