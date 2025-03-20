import numpy as np
import pandas as pd
from flask import Flask, render_template, request, json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import datetime
import warnings
import os
from sklearn.exceptions import InconsistentVersionWarning
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv('.env') if os.path.exists('.env') else None

# Suppress warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load models and data
with open('nlp_model.pkl', 'rb') as f:
    clf = pickle.load(f)

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')

# Utility functions
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list

def convert_to_list_num(my_list):
    my_list = my_list.split(',')
    my_list[0] = my_list[0].replace("[", "")
    my_list[-1] = my_list[-1].replace("]", "")
    return [int(i) if i.strip().isdigit() else i.strip() for i in my_list]

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

# Flask application
app = Flask(__name__)

@app.route("/health")
def health_check():
    return "OK", 200  

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', suggestions=get_suggestions())

@app.route("/populate-matches", methods=["POST"])
def populate_matches():
    res = json.loads(request.get_data("data"))
    movies_list = res['movies_list']
    
    movie_cards = {
        ("https://image.tmdb.org/t/p/original" + movie['poster_path'] if movie['poster_path'] 
         else "/static/movie_placeholder.jpeg"): [
             movie['title'],
             movie['original_title'],
             movie['vote_average'],
             datetime.strptime(movie['release_date'], '%Y-%m-%d').year if movie['release_date'] else "N/A",
             movie['id']
         ] for movie in movies_list
    }
    
    return render_template('recommend.html', movie_cards=movie_cards)

# API Proxy Endpoints
@app.route("/api/search")
def handle_search():
    query = request.args.get('query')
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    return requests.get(url).json()

@app.route("/api/movie/<int:movie_id>")
def handle_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

@app.route("/api/movie/<int:movie_id>/recommendations")
def handle_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

@app.route("/api/movie/<int:movie_id>/credits")
def handle_credits(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

@app.route("/api/person/<int:person_id>")
def handle_person(person_id):
    url = f"https://api.themoviedb.org/3/person/{person_id}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

# Main recommendation endpoint
@app.route("/recommend", methods=["POST"])
def recommend():
    # Extract form data
    form_fields = [
        'title', 'cast_ids', 'cast_names', 'cast_chars', 'cast_bdays',
        'cast_bios', 'cast_places', 'cast_profiles', 'imdb_id', 'poster',
        'genres', 'overview', 'rating', 'vote_count', 'rel_date',
        'release_date', 'runtime', 'status', 'rec_movies', 'rec_posters',
        'rec_movies_org', 'rec_year', 'rec_vote', 'rec_ids'
    ]
    form_data = {field: request.form[field] for field in form_fields}

    # Convert string data to proper formats
    conversions = {
        'rec_movies_org': convert_to_list,
        'rec_movies': convert_to_list,
        'rec_posters': convert_to_list,
        'cast_names': convert_to_list,
        'cast_chars': convert_to_list,
        'cast_profiles': convert_to_list,
        'cast_bdays': convert_to_list,
        'cast_bios': convert_to_list,
        'cast_places': convert_to_list,
        'cast_ids': convert_to_list_num,
        'rec_vote': convert_to_list_num,
        'rec_year': convert_to_list_num,
        'rec_ids': convert_to_list_num
    }

    for key, func in conversions.items():
        form_data[key] = func(form_data[key])

    # Process escape sequences
    for i in range(len(form_data['cast_bios'])):
        form_data['cast_bios'][i] = form_data['cast_bios'][i].replace(r'\n', '\n').replace(r'\"', '"')
        form_data['cast_chars'][i] = form_data['cast_chars'][i].replace(r'\n', '\n').replace(r'\"', '"')

    # Prepare data for template
    movie_cards = {form_data['rec_posters'][i]: [
        form_data['rec_movies'][i],
        form_data['rec_movies_org'][i],
        form_data['rec_vote'][i],
        form_data['rec_year'][i],
        form_data['rec_ids'][i]
    ] for i in range(len(form_data['rec_posters']))}

    casts = {form_data['cast_names'][i]: [
        form_data['cast_ids'][i],
        form_data['cast_chars'][i],
        form_data['cast_profiles'][i]
    ] for i in range(len(form_data['cast_profiles']))}

    cast_details = {form_data['cast_names'][i]: [
        form_data['cast_ids'][i],
        form_data['cast_profiles'][i],
        form_data['cast_bdays'][i],
        form_data['cast_places'][i],
        form_data['cast_bios'][i]
    ] for i in range(len(form_data['cast_places']))}

    # Handle reviews
    movie_reviews = {}
    if form_data['rec_ids']:
        try:
            movie_id = form_data['rec_ids'][0]
            url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
            reviews_data = requests.get(url).json()
            
            reviews_list = []
            reviews_status = []
            for review in reviews_data.get('results', [])[:10]:
                if review.get('content'):
                    review_text = review['content']
                    reviews_list.append(review_text)
                    pred = clf.predict([review_text])
                    reviews_status.append('Positive' if pred[0] else 'Negative')
            
            movie_reviews = dict(zip(reviews_list, reviews_status))
            
        except Exception as e:
            print(f"Error fetching reviews: {str(e)}")
            movie_reviews = {"Error": "Could not fetch reviews"}

    # Date handling
    movie_rel_date = datetime.strptime(form_data['rel_date'], '%Y-%m-%d') if form_data['rel_date'] else None
    curr_date = datetime.now()

    return render_template(
        'recommend.html',
        title=form_data['title'],
        poster=form_data['poster'],
        overview=form_data['overview'],
        vote_average=form_data['rating'],
        vote_count=form_data['vote_count'],
        release_date=form_data['release_date'],
        movie_rel_date=movie_rel_date,
        curr_date=curr_date,
        runtime=form_data['runtime'],
        status=form_data['status'],
        genres=form_data['genres'],
        movie_cards=movie_cards,
        reviews=movie_reviews,
        casts=casts,
        cast_details=cast_details
    )

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', False))