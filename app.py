from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# MongoDB Setup
client = MongoClient('mongodb+srv://Aishwarya:aishu%402004@cluster-1.tjgkz2l.mongodb.net/?retryWrites=true&w=majority')
db = client['movie_db']
movies_collection = db['movies']

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def normalize_genre(genre):
    return genre.strip().lower().capitalize()

@app.route('/')
def index():
    all_movies = list(movies_collection.find())
    genres = sorted(set(normalize_genre(movie['genre']) for movie in all_movies if 'genre' in movie))
    return render_template('index.html', all_movies=all_movies, genres=genres)

@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        genre = normalize_genre(request.form['genre'])
        location = request.form['location']
        meta_description = request.form['meta_description']
        reviews = request.form['reviews'].split(',')[:5]
        image = request.files['image']

        filename = ""
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        movie = {
            'title': title,
            'genre': genre,
            'location': location,
            'meta_description': meta_description,
            'reviews': reviews,
            'image_filename': filename
        }

        movies_collection.insert_one(movie)
        return redirect(url_for('index'))

    return render_template('add_movie.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    genres = sorted(set(normalize_genre(movie['genre']) for movie in movies_collection.find()))
    movies = movies_collection.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"genre": {"$regex": query, "$options": "i"}},
            {"location": {"$regex": query, "$options": "i"}},
            {"meta_description": {"$regex": query, "$options": "i"}}
        ]
    })
    return render_template('search_results.html', movies=movies, query=query, genres=genres)

@app.route('/genre/<genre_name>')
def genre_movies(genre_name):
    genre_name = normalize_genre(genre_name)
    movies = movies_collection.find({"genre": genre_name})
    genres = sorted(set(normalize_genre(movie['genre']) for movie in movies_collection.find()))
    return render_template('genre.html', genre=genre_name, movies=movies, genres=genres)

@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
    if not movie:
        return "", 404
    genres = sorted(set(normalize_genre(movie['genre']) for movie in movies_collection.find()))
    return render_template('movie_detail.html', movie=movie, genres=genres)

if __name__ == '__main__':
    app.run(debug=True)
