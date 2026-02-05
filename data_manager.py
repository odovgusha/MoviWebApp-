from models import db, User, Movie

class DataManager:

    def create_user(self, name):
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user

    def get_users(self):
        return User.query.all()

    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, movie):
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if not movie:
            return None
        movie.name = new_title
        db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            return False
        db.session.delete(movie)
        db.session.commit()
        return True
