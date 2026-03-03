from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Movie
from data_manager import DataManager
import os
import requests
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, "data"), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()


# HTTP ERROR HANDLERS


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


# ROUTES

@app.route('/')
def index():
    try:
        users = data_manager.get_users()
        return render_template('index.html', users=users)
    except Exception:
        return render_template('500.html'), 500


@app.route('/users', methods=['POST'])
def create_user():
    try:
        name = request.form.get('name', '').strip()
        if name:
            data_manager.create_user(name)
        return redirect(url_for('index'))
    except Exception:
        return render_template('500.html'), 500


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def get_movies(user_id):

    user = User.query.get_or_404(user_id)

    try:
        if request.method == 'POST':
            title = request.form.get('title', '').strip()

            if title:
                existing_movie = Movie.query.filter_by(
                    user_id=user.id,
                    name=title
                ).first()

                if existing_movie:
                    return render_template(
                        'movies.html',
                        user=user,
                        movies=data_manager.get_movies(user.id),
                        message=f"Movie '{title}' already exists!"
                    )

                response = requests.get(
                    "https://www.omdbapi.com/",
                    params={"t": title, "apikey": OMDB_API_KEY},
                    timeout=5
                )
                response.raise_for_status()

                data = response.json()

                if data.get("Response") == "False":
                    return render_template(
                        'movies.html',
                        user=user,
                        movies=data_manager.get_movies(user.id),
                        message=f"Movie '{title}' not found in OMDB!"
                    )

                movie = Movie(
                    name=data.get("Title"),
                    director=data.get("Director"),
                    year=data.get("Year"),
                    poster_url=data.get("Poster"),
                    score=data.get("imdbRating"),
                    user_id=user.id
                )

                data_manager.add_movie(movie)

            return redirect(url_for('get_movies', user_id=user.id))

        movies = data_manager.get_movies(user.id)
        return render_template('movies.html', user=user, movies=movies)

    except requests.exceptions.RequestException:
        return render_template(
            'movies.html',
            user=user,
            movies=data_manager.get_movies(user.id),
            message="Error connecting to OMDB service."
        )


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    try:
        new_title = request.form.get('new_title', '').strip()
        if new_title:
            data_manager.update_movie(movie_id, new_title)
        return redirect(url_for('get_movies', user_id=user_id))
    except Exception:
        return render_template('500.html'), 500


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(movie_id)
        return redirect(url_for('get_movies', user_id=user_id))
    except Exception:
        return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
