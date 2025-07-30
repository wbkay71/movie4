# 🎬 MoviWeb App

A modern, multi-user movie database web application built with Flask and SQLAlchemy. Users can create personal movie collections with automatic data fetching from the OMDb API.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-v3.1.1-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 📋 Features

### Core Functionality
- **Multi-User Support**: Multiple users can register and maintain separate movie collections
- **OMDb API Integration**: Automatic fetching of movie details including posters, directors, years, and ratings
- **Dual Rating System**: Display both OMDb ratings and personal user ratings
- **Full CRUD Operations**: Create, Read, Update, and Delete movies and users
- **Smart Search**: Search for movies with visual results before adding to collection
- **Responsive Design**: Mobile-friendly interface with Netflix-inspired dark theme

### Additional Features
- User deletion with cascade (removes all associated movies)
- Click-to-rate functionality for quick rating updates
- Intelligent rating display (shows `8` instead of `8.0`)
- Flash messages for user feedback
- Custom 404 error page
- Automatic current year in footer

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- OMDb API key (free from [OMDb API](http://www.omdbapi.com/apikey.aspx))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/movie4.git
   cd movie4
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OMDb API key
   OMDB_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
MoviWebApp/
├── app.py              # Main Flask application
├── models.py           # Database models (User, Movie)
├── data_manager.py     # Database operations handler
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
├── README.md          # Project documentation
├── static/            # Static assets
│   └── styles.css     # Application styles
├── templates/         # HTML templates
│   ├── base.html      # Base template with navigation
│   ├── index.html     # User list page
│   ├── movies.html    # Movie collection page
│   ├── search_movies.html  # Movie search results
│   ├── update_movie.html   # Movie edit form
│   └── 404.html       # Error page
└── instance/          # Local data (auto-created)
    └── movies.db      # SQLite database
```

## 💻 Usage

### Managing Users
1. **Add User**: Enter name on homepage and click "Add User"
2. **View Movies**: Click on any username to see their collection
3. **Delete User**: Click the delete button next to username (removes all their movies)

### Managing Movies
1. **Add Movie**: 
   - Enter movie title and click "Add Movie"
   - Select from search results with poster preview
   - Movie details are fetched automatically from OMDb
   
2. **Rate Movie**: 
   - Click on "Click to rate" or existing rating
   - Enter your personal rating (0-10)
   - OMDb rating is displayed but not editable

3. **Update Movie**: Click "Update" to edit movie details

4. **Delete Movie**: Click "Delete" to remove from collection

## 🎨 Design Features

- **Dark Theme**: Netflix-inspired color scheme for comfortable viewing
- **Responsive Grid**: Movie cards adapt to screen size
- **Visual Feedback**: Hover effects and animations
- **Clean Typography**: Easy-to-read text with proper hierarchy
- **Loading States**: Clear feedback during API calls

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OMDB_API_KEY` | Your OMDb API key | Yes |
| `FLASK_SECRET_KEY` | Flask session secret | Yes |
| `DEBUG` | Enable debug mode (`True`/`False`) | No |

### Database
The application uses SQLite for data storage. The database file is automatically created in the `instance/` directory on first run.

## 🧪 Development

### Running in Debug Mode
```bash
# In .env file
DEBUG=True
```

### Database Reset
```bash
# Delete existing database
rm instance/movies.db

# Run app to recreate
python app.py
```

### Adding New Features
1. Update models in `models.py`
2. Add operations in `data_manager.py`
3. Create routes in `app.py`
4. Add templates and update styles

## 📝 API Reference

### Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage with user list |
| POST | `/users` | Create new user |
| GET | `/users/<id>/movies` | View user's movies |
| POST | `/users/<id>/movies` | Search for movies |
| GET | `/users/<id>/movies/search` | Search results |
| GET | `/users/<id>/movies/add/<imdb_id>` | Add specific movie |
| GET | `/users/<id>/movies/<id>/update` | Update form |
| POST | `/users/<id>/movies/<id>/update` | Update movie |
| POST | `/users/<id>/movies/<id>/delete` | Delete movie |
| POST | `/users/<id>/delete` | Delete user |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built as part of the Masterschool Web Development Bootcamp
- Movie data provided by [OMDb API](http://www.omdbapi.com/)
- Icons from emoji Unicode standard
- Inspired by Netflix's UI/UX design

## 📞 Contact

Your Name - [@wbkay71](https://www.linkedin.com/in/wanja-benjamin-kneib-a6345851/)

Project Link: [https://github.com/yourusername/movie4](https://github.com/wbkay71/movie4)

---

Made with ❤️ and ☕ by a passionate developer
