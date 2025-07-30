"""Data management operations for MoviWebApp."""

from models import db, User, Movie


class DataManager:
    """Handles all database operations for users and movies."""

    def __init__(self):
        """Initialize DataManager."""
        pass

    # User operations
    def add_user(self, name):
        """
        Add a new user to the database.

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

    def get_all_users(self):
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

    def delete_user(self, user_id):
        """
        Delete a user and all associated movies.

        Args:
            user_id (int): The user's ID to delete

        Returns:
            bool: True if deleted, False if user not found
        """
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return False

        # Delete user (movies are deleted automatically due to cascade)
        db.session.delete(user)
        db.session.commit()

        return True

    # Movie operations
    def get_user_movies(self, user_id):
        """
        Get all movies for a specific user.

        Args:
            user_id (int): The user's ID

        Returns:
            list: List of Movie objects for this user
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, user_id, title, director, year, rating, poster=None, imdb_id=None):
        """
        Add a new movie for a user.

        Args:
            user_id (int): The user's ID
            title (str): Movie title
            director (str): Movie director
            year (int): Release year
            rating (float): OMDb rating
            poster (str, optional): Poster URL
            imdb_id (str, optional): IMDb ID

        Returns:
            Movie: The created Movie object or None if user not found
        """
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return None

        # Create new movie with OMDb data
        new_movie = Movie(
            title=title,
            director=director,
            year=year,
            rating=rating,  # OMDb rating
            user_rating=None,  # User rating starts as None
            poster=poster,
            imdb_id=imdb_id,
            user_id=user_id
        )

        # Add to database
        db.session.add(new_movie)
        db.session.commit()

        return new_movie

    def update_movie(self, movie_id, title, director, year, user_rating):
        """
        Update an existing movie (but NOT the OMDb rating).

        Args:
            movie_id (int): The movie's ID
            title (str): New title
            director (str): New director
            year (int): New year
            user_rating (float): User's personal rating

        Returns:
            Movie: Updated Movie object or None if not found
        """
        # Get the movie
        movie = Movie.query.get(movie_id)
        if not movie:
            return None

        # Update fields (but NOT the OMDb rating!)
        movie.title = title
        movie.director = director
        movie.year = year
        movie.user_rating = user_rating  # Update user's personal rating
        # movie.rating stays unchanged - it's the OMDb rating

        # Save changes
        db.session.commit()

        return movie

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.

        Args:
            movie_id (int): The movie's ID

        Returns:
            bool: True if deleted, False if movie not found
        """
        # Get the movie
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        # Delete from database
        db.session.delete(movie)
        db.session.commit()

        return True