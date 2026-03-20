import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

from data_loader import load_all_data, create_user_item_matrix


class CollaborativeRecommender:
    def __init__(self, ratings: pd.DataFrame, movies: pd.DataFrame, n_factors: int = 50):
        self.ratings = ratings
        self.movies = movies
        self.n_factors = n_factors

        self.user_item_matrix = create_user_item_matrix(ratings)
        self.user_ids = self.user_item_matrix.index.tolist()
        self.movie_ids = self.user_item_matrix.columns.tolist()

        self.user_to_idx = {uid: idx for idx, uid in enumerate(self.user_ids)}
        self.movie_to_idx = {mid: idx for idx, mid in enumerate(self.movie_ids)}
        self.idx_to_movie = {idx: mid for mid, idx in self.movie_to_idx.items()}

        self.movie_id_to_title = dict(zip(movies['movieId'], movies['title']))
        self.movie_id_to_genres = dict(zip(movies['movieId'], movies['genres']))

        self._train()

    def _train(self):
        matrix = self.user_item_matrix.fillna(0).values
        user_means = np.nanmean(np.where(matrix == 0, np.nan, matrix), axis=1)
        user_means = np.nan_to_num(user_means, nan=3.0)
        matrix_centered = matrix - user_means.reshape(-1, 1)

        sparse_matrix = csr_matrix(matrix_centered)
        k = min(self.n_factors, min(sparse_matrix.shape) - 1)
        U, sigma, Vt = svds(sparse_matrix, k=k)

        sigma = np.diag(sigma)
        self.predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_means.reshape(-1, 1)

        self.movie_avg_ratings = self.ratings.groupby('movieId')['rating'].mean().to_dict()

    def get_recommendations(self, user_id: int, n: int = 10) -> list[dict]:
        if user_id not in self.user_to_idx:
            return []

        user_idx = self.user_to_idx[user_id]
        user_predictions = self.predicted_ratings[user_idx]

        rated_movies = set(self.ratings[self.ratings['userId'] == user_id]['movieId'])

        predictions = []
        for idx, pred_rating in enumerate(user_predictions):
            movie_id = self.idx_to_movie[idx]
            if movie_id not in rated_movies:
                predictions.append((movie_id, pred_rating))

        predictions.sort(key=lambda x: x[1], reverse=True)
        top_n = predictions[:n]

        user_top_rated = self._get_user_top_movies(user_id)

        results = []
        for movie_id, pred_rating in top_n:
            avg_rating = self.movie_avg_ratings.get(movie_id, 3.0)
            explanation = self._build_explanation(pred_rating, avg_rating, user_top_rated)

            results.append({
                'movieId': movie_id,
                'title': self.movie_id_to_title.get(movie_id, f'Movie {movie_id}'),
                'genres': self.movie_id_to_genres.get(movie_id, ''),
                'predicted_rating': round(pred_rating, 2),
                'avg_rating': round(avg_rating, 2),
                'explanation': explanation
            })

        return results

    def _get_user_top_movies(self, user_id: int, n: int = 3) -> list[str]:
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        top = user_ratings.nlargest(n, 'rating')
        return [self.movie_id_to_title.get(mid, '') for mid in top['movieId']]

    def _build_explanation(self, pred_rating: float, avg_rating: float, user_top_movies: list) -> str:
        parts = []
        parts.append(f"Users with similar taste rated this {avg_rating:.1f}/5")
        if pred_rating > 4:
            parts.append("strong match with your preferences")
        elif pred_rating > 3.5:
            parts.append("good match with your preferences")
        return " — ".join(parts)

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        if user_id not in self.user_to_idx or movie_id not in self.movie_to_idx:
            return self.movie_avg_ratings.get(movie_id, 3.0)
        user_idx = self.user_to_idx[user_id]
        movie_idx = self.movie_to_idx[movie_id]
        return self.predicted_ratings[user_idx, movie_idx]


if __name__ == '__main__':
    movies, ratings = load_all_data()
    recommender = CollaborativeRecommender(ratings, movies)

    test_user = 42
    print('=' * 60)
    print(f'Collaborative filtering recommendations for user {test_user}')
    print('=' * 60)

    recs = recommender.get_recommendations(test_user, n=5)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Predicted: {rec['predicted_rating']}/5 | Avg: {rec['avg_rating']}/5")
        print(f"   {rec['explanation']}")
