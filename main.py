import numpy as np
import pandas as pd
from flask import Flask, render_template, request, json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import datetime
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Suppress warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load your pre-fitted sentiment analysis pipeline
with open('nlp_model.pkl', 'rb') as f:
    clf = pickle.load(f)

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

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions)

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

@app.route("/recommend", methods=["POST"])
def recommend():
    # Get form data
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    rel_date = request.form['rel_date']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies_org = request.form['rec_movies_org']
    rec_year = request.form['rec_year']
    rec_vote = request.form['rec_vote']
    rec_ids = request.form['rec_ids']

    # Convert data to proper formats
    rec_movies_org = convert_to_list(rec_movies_org)
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    cast_ids = convert_to_list_num(cast_ids)
    rec_vote = convert_to_list_num(rec_vote)
    rec_year = convert_to_list_num(rec_year)
    rec_ids = convert_to_list_num(rec_ids)

    # Process escape sequences in bios and characters
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '"')
        cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"', '"')

    movie_cards = {rec_posters[i]: [rec_movies[i], rec_movies_org[i], rec_vote[i], rec_year[i], rec_ids[i]] 
                   for i in range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] 
             for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] 
                    for i in range(len(cast_places))}

    # Fetch and analyze reviews from TMDB
    movie_reviews = {}
    TMDB_API_KEY = "46bb9f01f553c4675106157025eaf420"
    
    if rec_ids:
        try:
            movie_id = rec_ids[0]
            url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            
            reviews_data = response.json()
            reviews_list = []
            reviews_status = []
            
            for review in reviews_data.get('results', [])[:10]:
                if review.get('content'):
                    review_text = review['content']
                    reviews_list.append(review_text)
                    
                    # Fix: Pass text directly as a list
                    pred = clf.predict([review_text])
                    reviews_status.append('Positive' if pred[0] else 'Negative')
            
            movie_reviews = dict(zip(reviews_list, reviews_status))
            
        except Exception as e:
            print(f"Error fetching TMDB reviews: {str(e)}")
            movie_reviews = {"Error": "Could not fetch reviews at this time"}

    # Date handling
    movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d') if rel_date else None
    curr_date = datetime.now()

    return render_template(
        'recommend.html',
        title=title,
        poster=poster,
        overview=overview,
        vote_average=vote_average,
        vote_count=vote_count,
        release_date=release_date,
        movie_rel_date=movie_rel_date,
        curr_date=curr_date,
        runtime=runtime,
        status=status,
        genres=genres,
        movie_cards=movie_cards,
        reviews=movie_reviews,
        casts=casts,
        cast_details=cast_details
    )

if __name__ == '__main__':
    app.run(debug=True)