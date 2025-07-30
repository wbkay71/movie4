"""Main Flask application for MoviWebApp."""

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from models import db, Movie
from data_manager import DataManager

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Create DataManager instance
data_manager = DataManager()


# Create tables before first request
def create_tables():
    """Create database tables if they don't exist."""
    with app.app_context():
        db.create_all()


# Routes
@app.route('/')
def index():
    """Home page - display all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    name = request.form.get('name')
    if name:
        data_manager.create_user(name)
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    """Display all movies for a specific user."""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a new movie for a user."""
    # For now, just get the title
    # Later we'll add OMDb API integration
    title = request.form.get('title')

    if title:
        # Create movie object
        new_movie = Movie(
            name=title,
            user_id=user_id
        )
        data_manager.add_movie(new_movie)

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update a movie's title."""
    new_title = request.form.get('title')
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Create tables before running
    create_tables()

    # Run the app
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true')