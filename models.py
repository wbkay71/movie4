"""Database models for MoviWebApp."""

from flask_sqlalchemy import SQLAlchemy

# Create database instance
db = SQLAlchemy()


class User(db.Model):
    """User model - represents a user in the system."""
    # Explicitly set table name to match foreign key reference
    __tablename__ = 'users'

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
    """Movie model - represents a movie in the database."""
    # Explicitly set table name
    __tablename__ = 'movies'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Movie information
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster = db.Column(db.String(300))
    imdb_id = db.Column(db.String(20))

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        """String representation of Movie object."""
        return f'<Movie {self.title}>'  # Changed from self.name to self.title