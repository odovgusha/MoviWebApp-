from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Movie
from data_manager import DataManager
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()




@app.route('/')
def index():
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('name')
    if name:
        data_manager.create_user(name)
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def user_movies(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            response = requests.get(
                "http://www.omdbapi.com/",
                params={"t": title, "apikey": OMDB_API_KEY}
            )
            data = response.json()

            movie = Movie(
                name=title,
                director=data.get("Director"),
                year=data.get("Year"),
                poster_url=data.get("Poster"),
                user_id=user.id
            )
            data_manager.add_movie(movie)

        return redirect(url_for('user_movies', user_id=user.id))

    movies = data_manager.get_movies(user.id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    new_title = request.form.get('new_title')
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
