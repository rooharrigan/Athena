from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
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


class User(db.Model):
    """Stores user id and email information."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    avg_score = db.Column(db.Integer, nullable=True)
    quizzes_taken = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        return "<User id=%d email=%s>" % (self.id, self.email)


    def add_quiz_taken(self):
        """"""
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
    score = db.Column(db.String, nullable=True)

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

