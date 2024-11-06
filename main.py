from flask import Flask, jsonify, request, abort
import pandas as pd

app = Flask(__name__)

# Load CSV files 
movies_df = pd.read_csv('data/movies.csv')
ratings_df = pd.read_csv('data/ratings.csv')
tags_df = pd.read_csv('data/tags.csv')
links_df = pd.read_csv('data/links.csv')

# Paginate results
def paginate(df, page, per_page):
    total = len(df)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return df.iloc[start:end].to_dict(orient='records'), pages

#Filter data by movieId
def filter_by_movie_id(df, movie_id):
    return df[df['movieId'] == movie_id].to_dict(orient='records')

#Validate and parse request arguments
def parse_pagination_args():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        if page < 1 or per_page < 1:
            raise ValueError("Page and per_page must be positive integers.")
    except ValueError as e:
        abort(400, description=f"Invalid pagination parameters: {str(e)}")
    return page, per_page

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An unexpected error occurred"}), 500

# Movies Endpoint
@app.route('/movies', methods=['GET'])
def get_movies():
    # Search and filtering
    title_search = request.args.get('title')
    genre_filter = request.args.get('genre')
    movies = movies_df

    # Filter by title
    if title_search:
        movies = movies[movies['title'].str.contains(title_search, case=False, na=False)]

    # Filter by genre
    if genre_filter:
        movies = movies[movies['genres'].str.contains(genre_filter, case=False, na=False)]

    # Pagination
    page, per_page = parse_pagination_args()
    paginated_movies, pages = paginate(movies, page, per_page)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_pages": pages,
        "total_items": len(movies),
        "movies": paginated_movies
    }), 200

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    movie = filter_by_movie_id(movies_df, movie_id)
    if not movie:
        return not_found(f"Movie with ID {movie_id} not found")
    return jsonify(movie[0]), 200

# Ratings Endpoint
@app.route('/ratings', methods=['GET'])
def get_ratings():
    page, per_page = parse_pagination_args()
    paginated_ratings, pages = paginate(ratings_df, page, per_page)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_pages": pages,
        "total_items": len(ratings_df),
        "ratings": paginated_ratings
    }), 200

@app.route('/ratings/<int:movie_id>', methods=['GET'])
def get_ratings_by_movie(movie_id):
    ratings = filter_by_movie_id(ratings_df, movie_id)
    if not ratings:
        return not_found(f"Ratings for movie ID {movie_id} not found")
    return jsonify(ratings), 200

# Tags Endpoint
@app.route('/tags', methods=['GET'])
def get_tags():
    page, per_page = parse_pagination_args()
    paginated_tags, pages = paginate(tags_df, page, per_page)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_pages": pages,
        "total_items": len(tags_df),
        "tags": paginated_tags
    }), 200

@app.route('/tags/<int:movie_id>', methods=['GET'])
def get_tags_by_movie(movie_id):
    tags = filter_by_movie_id(tags_df, movie_id)
    if not tags:
        return not_found(f"Tags for movie ID {movie_id} not found")
    return jsonify(tags), 200

# Links Endpoint
@app.route('/links', methods=['GET'])
def get_links():
    page, per_page = parse_pagination_args()
    paginated_links, pages = paginate(links_df, page, per_page)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_pages": pages,
        "total_items": len(links_df),
        "links": paginated_links
    }), 200

@app.route('/links/<int:movie_id>', methods=['GET'])
def get_link_by_movie(movie_id):
    link = filter_by_movie_id(links_df, movie_id)
    if not link:
        return not_found(f"Link for movie ID {movie_id} not found")
    return jsonify(link[0]), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
