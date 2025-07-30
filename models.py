"""Database models for MoviWebApp."""

from flask_sqlalchemy import SQLAlchemy

# Create database instance
db = SQLAlchemy()


class User(db.Model):
    """User model - represents a user in the system."""

    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User's name - cannot be empty
    name = db.Column(db.String(100), nullable=False)

    # Relationship to movies - one user can have many movies
    movies = db.relationship('Movie', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.name}>'


class Movie(db.Model):
    """Movie model - represents a user's favorite movie."""

    # Primary key - unique identifier for each movie
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Movie details
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))

    # Foreign key - links movie to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        """String representation of Movie object."""
        return f'<Movie {self.name}>'