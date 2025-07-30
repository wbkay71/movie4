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

# Search functionality for multiple movies
def search_movies_from_api(query):
    """Search for multiple movies from OMDb API.

    Args:
        query (str): Search query for movies

    Returns:
        list: List of movie results with basic info
    """
    # Check if API key is configured
    if not OMDB_API_KEY:
        print("Warning: OMDB_API_KEY not set in environment variables")
        return []

    try:
        # Prepare API request parameters for search
        params = {
            'apikey': OMDB_API_KEY,
            's': query,  # 's' parameter searches for multiple results
            'type': 'movie'  # Only search for movies
        }

        # Make API request
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Check if search was successful
        if data.get('Response') == 'True':
            # Extract search results
            movies = []
            for movie in data.get('Search', []):
                movies.append({
                    'title': movie.get('Title', ''),
                    'year': movie.get('Year', ''),
                    'imdb_id': movie.get('imdbID', ''),
                    'poster': movie.get('Poster') if movie.get('Poster') != 'N/A' else None
                })
            return movies[:10]  # Limit to 10 results
        else:
            print(f"No movies found for '{query}'")
            return []

    except requests.RequestException as e:
        print(f"Error searching OMDb API: {e}")
        return []

# This context processor eliminates the need to pass current_year
# to every render_template() call. It's automatically available
# in all templates as {{ current_year }}
@app.context_processor
def inject_year():
    """Make current year available in all templates"""
    return {'current_year': datetime.now().year}

# Custom template filter for rating display
@app.template_filter('format_rating')
def format_rating(rating, show_na=False):
    """Format rating to show clean numbers.

    Args:
        rating (float): The rating value
        show_na (bool): Whether to show 'N/A' for missing ratings

    Returns:
        str: Formatted rating string
    """
    # Handle None or 0 ratings
    if rating is None or rating == 0:
        return "N/A" if show_na else "0"

    # If rating is a whole number, show without decimal
    if float(rating) == int(rating):
        return str(int(rating))
    else:
        # Show one decimal place for fractional ratings
        return f"{rating:.1f}"

# Create tables before first request
def create_tables():
    """Create database tables if they don't exist."""
    with app.app_context():
        db.create_all()


# Routes
@app.route('/')
def index():
    """Home page - display all users."""
    users = data_manager.get_all_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    name = request.form.get('name')
    if name:
        data_manager.add_user(name)
        flash('User added successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    """Display all movies for a specific user."""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return render_template('404.html'), 404

    movies = data_manager.get_user_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)

# Movie routes
@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Search for movies instead of direct add."""
    # Get search query
    title = request.form.get('title', '').strip()

    if not title:
        flash('Please enter a movie title!', 'error')
        return redirect(url_for('user_movies', user_id=user_id))

    # Redirect to search page
    return redirect(url_for('search_movies', user_id=user_id, q=title))

# Movie search route
@app.route('/users/<int:user_id>/movies/search')
def search_movies(user_id):
    """Search for movies to add."""
    # Check if user exists
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return render_template('404.html'), 404

    # Get search query from URL parameters
    query = request.args.get('q', '').strip()

    if not query:
        flash('Please enter a movie title to search.', 'warning')
        return redirect(url_for('user_movies', user_id=user_id))

    # Search for movies
    search_results = search_movies_from_api(query)

    return render_template('search_movies.html',
                           user=user,
                           query=query,
                           movies=search_results)

# Add movie by specific IMDb ID
@app.route('/users/<int:user_id>/movies/add/<imdb_id>')
def add_movie_by_id(user_id, imdb_id):
    """Add a specific movie by IMDb ID."""
    # Check if user exists
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return render_template('404.html'), 404

    # Fetch specific movie details by IMDb ID
    try:
        params = {
            'apikey': OMDB_API_KEY,
            'i': imdb_id  # 'i' parameter searches by IMDb ID
        }

        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True':
            # Add movie with full details
            movie = data_manager.add_movie(
                user_id=user_id,
                title=data.get('Title', 'Unknown'),
                director=data.get('Director', 'Unknown'),
                year=int(data.get('Year', 0)) if data.get('Year', '').isdigit() else 0,
                rating=float(data.get('imdbRating', 0)) if data.get('imdbRating', 'N/A') != 'N/A' else 0.0,
                poster=data.get('Poster') if data.get('Poster') != 'N/A' else None,
                imdb_id=imdb_id
            )
            flash(f'Movie "{data.get("Title")}" added successfully!', 'success')
        else:
            flash('Could not fetch movie details.', 'error')

    except Exception as e:
        print(f"Error adding movie by ID: {e}")
        flash('Error adding movie.', 'error')

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
    user_rating = request.form.get('user_rating')  # NEW: Get user rating

    # Convert types
    try:
        year = int(year) if year else 0
        user_rating = float(user_rating) if user_rating else None  # Allow None for no rating
    except ValueError:
        year = 0
        user_rating = None

    # Update movie - now passing user_rating as 5th parameter
    data_manager.update_movie(movie_id, title, director, year, user_rating)
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