import pandas as pd

from data_loader import load_all_data
from content_based import ContentBasedRecommender
from collaborative import CollaborativeRecommender


class HybridRecommender:
    def __init__(self, movies: pd.DataFrame, ratings: pd.DataFrame,
                 content_weight: float = 0.3, collab_weight: float = 0.7):
        self.movies = movies
        self.ratings = ratings
        self.content_weight = content_weight
        self.collab_weight = collab_weight

        self.content_rec = ContentBasedRecommender(movies)
        self.collab_rec = CollaborativeRecommender(ratings, movies)

        self.movie_id_to_title = dict(zip(movies['movieId'], movies['title']))
        self.title_to_movie_id = dict(zip(movies['title'], movies['movieId']))

    def get_recommendations(self, user_id: int, n: int = 10) -> list[dict]:
        user_top_movies = self._get_user_favorites(user_id)
        if not user_top_movies:
            return self.collab_rec.get_recommendations(user_id, n)

        content_scores = {}
        content_explanations = {}
        for fav_title, fav_rating in user_top_movies:
            similar = self.content_rec.get_similar_movies(fav_title, n=20)
            for rec in similar:
                mid = rec['movieId']
                weighted_score = rec['score'] * (fav_rating / 5.0)
                if mid not in content_scores or weighted_score > content_scores[mid]:
                    content_scores[mid] = weighted_score
                    content_explanations[mid] = {
                        'source_movie': fav_title,
                        'shared_genres': rec['shared_genres'],
                        'shared_tags': rec['shared_tags']
                    }

        rated_movies = set(self.ratings[self.ratings['userId'] == user_id]['movieId'])

        candidates = {}
        for mid in set(content_scores.keys()) | set(self.collab_rec.movie_ids):
            if mid in rated_movies:
                continue

            c_score = content_scores.get(mid, 0)
            collab_pred = self.collab_rec.predict_rating(user_id, mid)
            collab_norm = (collab_pred - 1) / 4

            hybrid_score = self.content_weight * c_score + self.collab_weight * collab_norm
            candidates[mid] = {
                'hybrid_score': hybrid_score,
                'content_score': c_score,
                'collab_pred': collab_pred,
                'content_explanation': content_explanations.get(mid)
            }

        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1]['hybrid_score'], reverse=True)[:n]

        results = []
        for movie_id, scores in sorted_candidates:
            title = self.movie_id_to_title.get(movie_id, f'Movie {movie_id}')
            genres = self.movies[self.movies['movieId'] == movie_id]['genres'].iloc[0] if movie_id in self.movies['movieId'].values else ''
            avg_rating = self.collab_rec.movie_avg_ratings.get(movie_id, 3.0)

            explanation = self._build_explanation(
                scores['content_explanation'],
                scores['collab_pred'],
                avg_rating,
                user_top_movies
            )

            results.append({
                'movieId': movie_id,
                'title': title,
                'genres': genres,
                'score': round(scores['hybrid_score'], 2),
                'predicted_rating': round(scores['collab_pred'], 1),
                'explanation': explanation
            })

        return results

    def _get_user_favorites(self, user_id: int, n: int = 5, min_rating: float = 4.0) -> list[tuple[str, float]]:
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        top_rated = user_ratings[user_ratings['rating'] >= min_rating].nlargest(n, 'rating')
        return [(self.movie_id_to_title.get(mid, ''), rating)
                for mid, rating in zip(top_rated['movieId'], top_rated['rating'])
                if mid in self.movie_id_to_title]

    def _build_explanation(self, content_exp: dict, collab_pred: float,
                           avg_rating: float, user_favorites: list) -> str:
        lines = []

        if content_exp:
            source = content_exp['source_movie']
            genres = content_exp['shared_genres']
            tags = content_exp['shared_tags']

            genre_str = f"shares genres: {', '.join(genres)}" if genres else ""
            if genre_str:
                lines.append(f"Similar to {source} — {genre_str}")
            elif tags:
                lines.append(f"Similar themes to {source}")

        lines.append(f"Users with similar taste rated this {avg_rating:.1f}/5")

        return '\n       '.join(lines) if lines else "Recommended based on your viewing history"


if __name__ == '__main__':
    movies, ratings = load_all_data()
    recommender = HybridRecommender(movies, ratings)

    test_user = 42
    print('=' * 70)
    print(f'HYBRID RECOMMENDATIONS FOR USER {test_user}')
    print('=' * 70)

    user_favs = recommender._get_user_favorites(test_user)
    if user_favs:
        print(f"\nUser's top rated movies:")
        for title, rating in user_favs[:3]:
            print(f"  - {title} ({rating}/5)")

    print(f"\n{'='*70}")
    recs = recommender.get_recommendations(test_user, n=5)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']} | Predicted: {rec['predicted_rating']}/5")
        print(f"   Why: {rec['explanation']}")
