"""Data management operations for MoviWebApp."""

from models import db, User, Movie


class DataManager:
    """Handles all database operations for users and movies."""

    def __init__(self):
        """Initialize DataManager."""
        pass

    # User operations
    def create_user(self, name):
        """
        Create a new user in the database.

        Args:
            name (str): The name of the user

        Returns:
            User: The created user object
        """
        # Create new user instance
        new_user = User(name=name)

        # Add to database session and commit
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def get_users(self):
        """
        Get all users from the database.

        Returns:
            list: List of all User objects
        """
        return User.query.all()

    def get_user_by_id(self, user_id):
        """
        Get a specific user by ID.

        Args:
            user_id (int): The user's ID

        Returns:
            User: The user object or None if not found
        """
        return User.query.get(user_id)

    # Movie operations
    def get_movies(self, user_id):
        """
        Get all movies for a specific user.

        Args:
            user_id (int): The user's ID

        Returns:
            list: List of Movie objects for this user
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, movie):
        """
        Add a new movie to the database.

        Args:
            movie (Movie): Movie object to add
        """
        db.session.add(movie)
        db.session.commit()

    def update_movie(self, movie_id, new_title):
        """
        Update a movie's title.

        Args:
            movie_id (int): The movie's ID
            new_title (str): The new title for the movie

        Returns:
            bool: True if updated, False if movie not found
        """
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = new_title
            db.session.commit()
            return True
        return False

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.

        Args:
            movie_id (int): The movie's ID

        Returns:
            bool: True if deleted, False if movie not found
        """
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False