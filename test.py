import requests

def get_tmdb_reviews(movie_id, api_key, max_reviews=10):
    """
    Retrieve reviews for a movie from TMDB API.
    
    Args:
        movie_id (str or int): The TMDB movie ID.
        api_key (str): Your TMDB API key.
        max_reviews (int): Maximum number of reviews to retrieve.
    
    Returns:
        list: A list of review strings.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {
        "api_key": api_key,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to retrieve TMDB reviews")
        return []
    
    data = response.json()
    reviews = [review.get("content", "") for review in data.get("results", [])][:max_reviews]
    
    return reviews if reviews else ["No reviews found"]

# Example usage
api_key = "46bb9f01f553c4675106157025eaf420"  # Replace with your actual TMDB API key
movie_id = 550  # Example: TMDB movie ID for Fight Club
reviews = get_tmdb_reviews(movie_id, api_key, max_reviews=5)

for i, review in enumerate(reviews, 1):
    print(f"Review {i}: {review}\n")
#