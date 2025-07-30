"""Main Flask application for MoviWebApp."""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

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

# This context processor eliminates the need to pass current_year
# to every render_template() call. It's automatically available
# in all templates as {{ current_year }}
@app.context_processor
def inject_year():
    """Make current year available in all templates"""
    return {'current_year': datetime.now().year}

# Create tables before first request
def create_tables():
    """Create database tables if they don't exist."""
    with app.app_context():
        db.create_all()


# Routes
@app.route('/')
def index():
    """Home page - display all users."""
    users = data_manager.get_all_users()  # Fixed method name
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    name = request.form.get('name')
    if name:
        data_manager.add_user(name)  # Fixed method name
        flash('User added successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    """Display all movies for a specific user."""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return render_template('404.html'), 404

    movies = data_manager.get_user_movies(user_id)  # Fixed method name
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a new movie for a user."""
    # Get form data
    title = request.form.get('title')

    if title:
        # For now, add movie with basic info
        # OMDb API integration will be added later
        data_manager.add_movie(
            user_id=user_id,
            title=title,
            director='Unknown',  # Will be filled by OMDb API
            year=2024,          # Will be filled by OMDb API
            rating=0.0          # Will be filled by OMDb API
        )
        flash('Movie added successfully!', 'success')

    return redirect(url_for('user_movies', user_id=user_id))

# Movie update routes (GET for form, POST for processing)
@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['GET'])
def update_movie_form(user_id, movie_id):
    """Show form to update a movie."""
    # Get the movie
    movie = Movie.query.get(movie_id)
    if not movie or movie.user_id != user_id:
        return render_template('404.html'), 404

    # Get the user for template context
    user = data_manager.get_user_by_id(user_id)

    return render_template('update_movie.html', user=user, movie=movie)

@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update a movie's information."""
    # Get form data
    title = request.form.get('title')
    director = request.form.get('director')
    year = request.form.get('year')
    rating = request.form.get('rating')

    # Convert types
    try:
        year = int(year) if year else 0
        rating = float(rating) if rating else 0.0
    except ValueError:
        year = 0
        rating = 0.0

    # Update movie
    data_manager.update_movie(movie_id, title, director, year, rating)
    flash('Movie updated successfully!', 'success')

    return redirect(url_for('user_movies', user_id=user_id))

# Movie delete route
@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie."""
    data_manager.delete_movie(movie_id)
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('user_movies', user_id=user_id))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

# User delete route
@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user and all their movies."""
    # Check if user exists
    user = data_manager.get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('index'))

    # Delete the user
    if data_manager.delete_user(user_id):
        flash(f'User "{user.name}" deleted successfully!', 'success')
    else:
        flash('Error deleting user!', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    # Create tables before running
    create_tables()

    # Run the app
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true')