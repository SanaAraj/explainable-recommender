import pandas as pd

from data_loader import load_all_data
from content_based import ContentBasedRecommender
from collaborative import CollaborativeRecommender


class HybridRecommender:
    def __init__(self, movies: pd.DataFrame, ratings: pd.DataFrame,
                 content_weight: float = 0.4, collab_weight: float = 0.6):
        self.movies = movies
        self.ratings = ratings
        self.content_weight = content_weight
        self.collab_weight = collab_weight

        self.content_rec = ContentBasedRecommender(movies)
        self.collab_rec = CollaborativeRecommender(ratings, movies)

        self.movie_id_to_title = dict(zip(movies['movieId'], movies['title']))
        self.title_to_movie_id = dict(zip(movies['title'], movies['movieId']))

    def get_popular_movies(self, n: int = 30) -> list[dict]:
        rating_counts = self.ratings.groupby('movieId').agg(
            count=('rating', 'count'),
            avg_rating=('rating', 'mean')
        ).reset_index()

        popular = rating_counts[rating_counts['count'] >= 50].nlargest(n, 'count')

        results = []
        for _, row in popular.iterrows():
            movie_id = row['movieId']
            movie_data = self.movies[self.movies['movieId'] == movie_id].iloc[0]
            results.append({
                'movieId': int(movie_id),
                'title': movie_data['title'],
                'genres': movie_data['genres'],
                'rating_count': int(row['count']),
                'avg_rating': round(row['avg_rating'], 1)
            })
        return results

    def recommend_from_likes(self, liked_titles: list[str], n: int = 10) -> list[dict]:
        liked_ids = set()
        valid_titles = []
        for title in liked_titles:
            if title in self.title_to_movie_id:
                liked_ids.add(self.title_to_movie_id[title])
                valid_titles.append(title)

        if not valid_titles:
            return []

        content_scores = {}
        content_explanations = {}
        for title in valid_titles:
            similar = self.content_rec.get_similar_movies(title, n=30)
            for rec in similar:
                mid = rec['movieId']
                if mid in liked_ids:
                    continue
                if mid not in content_scores or rec['score'] > content_scores[mid]:
                    content_scores[mid] = rec['score']
                    content_explanations[mid] = {
                        'source_movie': title,
                        'shared_genres': rec['shared_genres'],
                        'shared_tags': rec['shared_tags']
                    }

        similar_users = self._find_similar_users(liked_ids)
        collab_scores = self._aggregate_user_preferences(similar_users, liked_ids)

        candidates = {}
        all_movie_ids = set(content_scores.keys()) | set(collab_scores.keys())

        for mid in all_movie_ids:
            if mid in liked_ids:
                continue

            c_score = content_scores.get(mid, 0)
            collab_data = collab_scores.get(mid, {'score': 0, 'avg_rating': 3.0, 'fan_count': 0})

            hybrid_score = self.content_weight * c_score + self.collab_weight * collab_data['score']
            candidates[mid] = {
                'hybrid_score': hybrid_score,
                'content_score': c_score,
                'collab_score': collab_data['score'],
                'avg_rating': collab_data['avg_rating'],
                'fan_count': collab_data['fan_count'],
                'content_explanation': content_explanations.get(mid)
            }

        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1]['hybrid_score'], reverse=True)[:n]

        results = []
        for movie_id, scores in sorted_candidates:
            title = self.movie_id_to_title.get(movie_id, f'Movie {movie_id}')
            movie_row = self.movies[self.movies['movieId'] == movie_id]
            genres = movie_row['genres'].iloc[0] if not movie_row.empty else ''

            explanation = self._build_liked_explanation(
                scores['content_explanation'],
                scores['avg_rating'],
                scores['fan_count'],
                valid_titles
            )

            results.append({
                'movieId': movie_id,
                'title': title,
                'genres': genres,
                'score': round(scores['hybrid_score'], 2),
                'avg_rating': round(scores['avg_rating'], 1),
                'explanation': explanation
            })

        return results

    def _find_similar_users(self, liked_movie_ids: set, min_overlap: int = 2) -> list[int]:
        user_liked = self.ratings[
            (self.ratings['movieId'].isin(liked_movie_ids)) &
            (self.ratings['rating'] >= 4.0)
        ]
        user_counts = user_liked.groupby('userId').size()
        similar_users = user_counts[user_counts >= min_overlap].index.tolist()
        return similar_users[:100]

    def _aggregate_user_preferences(self, user_ids: list[int], exclude_ids: set) -> dict:
        if not user_ids:
            return {}

        user_ratings = self.ratings[
            (self.ratings['userId'].isin(user_ids)) &
            (self.ratings['rating'] >= 4.0) &
            (~self.ratings['movieId'].isin(exclude_ids))
        ]

        agg = user_ratings.groupby('movieId').agg(
            avg_rating=('rating', 'mean'),
            fan_count=('userId', 'nunique')
        ).reset_index()

        if agg.empty:
            return {}

        max_fans = agg['fan_count'].max()
        result = {}
        for _, row in agg.iterrows():
            mid = row['movieId']
            normalized_score = row['fan_count'] / max_fans if max_fans > 0 else 0
            result[mid] = {
                'score': normalized_score,
                'avg_rating': row['avg_rating'],
                'fan_count': int(row['fan_count'])
            }
        return result

    def _build_liked_explanation(self, content_exp: dict, avg_rating: float,
                                  fan_count: int, liked_titles: list) -> str:
        parts = []

        if content_exp and content_exp.get('shared_genres'):
            source = content_exp['source_movie']
            genres = ', '.join(content_exp['shared_genres'])
            parts.append(f"Because you liked {source} — shares genres: {genres}")
        elif content_exp and content_exp.get('shared_tags'):
            source = content_exp['source_movie']
            parts.append(f"Similar themes to {source}")

        if fan_count > 1:
            parts.append(f"Fans of your picks rated this {avg_rating:.1f}/5")
        elif avg_rating > 0:
            parts.append(f"Average rating: {avg_rating:.1f}/5")

        return '. '.join(parts) if parts else "Recommended based on your selections"

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

    print('=' * 70)
    print('POPULAR MOVIES')
    print('=' * 70)
    popular = recommender.get_popular_movies(n=5)
    for m in popular:
        print(f"  {m['title']} - {m['rating_count']} ratings, avg {m['avg_rating']}")

    print(f"\n{'='*70}")
    print('RECOMMENDATIONS BASED ON LIKED MOVIES')
    print('=' * 70)

    liked = ['Toy Story (1995)', 'Jurassic Park (1993)', 'Forrest Gump (1994)']
    print(f"\nLiked movies: {liked}")
    print()

    recs = recommender.recommend_from_likes(liked, n=5)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Score: {rec['score']} | Avg rating: {rec['avg_rating']}/5")
        print(f"   Why: {rec['explanation']}")
        print()
