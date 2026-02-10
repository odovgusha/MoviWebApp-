from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    movies = db.relationship('Movie', backref='user', lazy=True)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    director = db.Column(db.String)
    year = db.Column(db.String)
    poster_url = db.Column(db.String)
    score = db.Column(db.String)  # <--- Add this line
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
