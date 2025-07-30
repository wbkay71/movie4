"""Main Flask application for MoviWebApp."""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import requests

from models import db, User, Movie
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

# Creating connection via API to movie database OMDB
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
OMDB_API_URL = 'http://www.omdbapi.com/'

# Fetching movie data via API from movie database OMDB
def fetch_movie_from_api(title):
    """Fetch movie details from OMDb API.

    Args:
        title (str): Movie title to search for

    Returns:
        dict: Movie data with title, director, year, rating, poster, imdb_id
        None: If movie not found or API error
    """
    # Check if API key is configured
    if not OMDB_API_KEY:
        print("Warning: OMDB_API_KEY not set in environment variables")
        return None

    try:
        # Prepare API request parameters
        params = {
            'apikey': OMDB_API_KEY,
            't': title,  # 't' parameter searches by title
            'type': 'movie'  # Only search for movies, not TV series
        }

        # Make API request
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse JSON response
        data = response.json()

        # Check if movie was found
        if data.get('Response') == 'True':
            # Extract and return relevant data
            return {
                'title': data.get('Title', title),
                'director': data.get('Director', 'Unknown'),
                'year': int(data.get('Year', 0)) if data.get('Year', '').isdigit() else 0,
                'rating': float(data.get('imdbRating', 0)) if data.get('imdbRating', 'N/A') != 'N/A' else 0.0,
                'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                'imdb_id': data.get('imdbID', '')
            }
        else:
            # Movie not found
            print(f"Movie '{title}' not found in OMDb: {data.get('Error', 'Unknown error')}")
            return None

    except requests.RequestException as e:
        # Network or API error
        print(f"Error fetching from OMDb API: {e}")
        return None
    except (ValueError, KeyError) as e:
        # Data parsing error
        print(f"Error parsing OMDb response: {e}")
        return None

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
    # Check if user exists
    user = data_manager.get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('index'))

    # Get form data
    title = request.form.get('title', '').strip()

    if not title:
        flash('Please enter a movie title!', 'error')
        return redirect(url_for('user_movies', user_id=user_id))

    # Try to fetch movie data from OMDb API
    api_data = fetch_movie_from_api(title)

    if api_data:
        # Use API data to create movie
        movie = data_manager.add_movie(
            user_id=user_id,
            title=api_data['title'],
            director=api_data['director'],
            year=api_data['year'],
            rating=api_data['rating'],
            poster=api_data['poster'],
            imdb_id=api_data['imdb_id']
        )
        flash(f'Movie "{api_data["title"]}" added successfully from OMDb!', 'success')
    else:
        # API failed or movie not found - add with basic info
        movie = data_manager.add_movie(
            user_id=user_id,
            title=title,
            director='Unknown',
            year=datetime.now().year,  # Default to current year
            rating=0.0,
            poster=None,
            imdb_id=None
        )
        flash(f'Movie "{title}" added manually (not found in OMDb).', 'warning')

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