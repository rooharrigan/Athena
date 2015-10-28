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

    name = db.Column(db.String, primary_key=True)
    capital = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<Country name=%s>" % (self.name)


class User(db.Model):
    """Stores user id and email information."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<User id=%d name=%s>" % (self.id, self.name)








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
