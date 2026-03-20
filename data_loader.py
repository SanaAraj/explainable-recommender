import os
import zipfile
import requests
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MOVIELENS_URL = 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip'


def download_movielens():
    if os.path.exists(os.path.join(DATA_DIR, 'ml-latest-small')):
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    zip_path = os.path.join(DATA_DIR, 'ml-latest-small.zip')

    print('Downloading MovieLens dataset...')
    response = requests.get(MOVIELENS_URL, stream=True)
    response.raise_for_status()

    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(DATA_DIR)

    os.remove(zip_path)
    print('Dataset downloaded and extracted.')


def load_movies():
    download_movielens()
    path = os.path.join(DATA_DIR, 'ml-latest-small', 'movies.csv')
    return pd.read_csv(path)


def load_ratings():
    download_movielens()
    path = os.path.join(DATA_DIR, 'ml-latest-small', 'ratings.csv')
    return pd.read_csv(path)


def load_tags():
    download_movielens()
    path = os.path.join(DATA_DIR, 'ml-latest-small', 'tags.csv')
    return pd.read_csv(path)


def load_all_data():
    movies = load_movies()
    ratings = load_ratings()
    tags = load_tags()

    # Aggregate tags per movie
    movie_tags = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x.astype(str).str.lower())).reset_index()
    movie_tags.columns = ['movieId', 'tags']

    # Merge movies with tags
    movies = movies.merge(movie_tags, on='movieId', how='left')
    movies['tags'] = movies['tags'].fillna('')

    return movies, ratings


def create_user_item_matrix(ratings):
    return ratings.pivot(index='userId', columns='movieId', values='rating')


if __name__ == '__main__':
    movies, ratings = load_all_data()
    print(f'Movies shape: {movies.shape}')
    print(f'Ratings shape: {ratings.shape}')
    print('\nSample movies:')
    print(movies.head())
    print('\nSample ratings:')
    print(ratings.head())

    matrix = create_user_item_matrix(ratings)
    print(f'\nUser-item matrix shape: {matrix.shape}')
