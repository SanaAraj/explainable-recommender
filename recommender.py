import json
import os
from collections import Counter

CATALOG_PATH = os.path.join(os.path.dirname(__file__), 'movies_catalog.json')


class MovieRecommender:
    def __init__(self):
        with open(CATALOG_PATH) as f:
            self.movies = json.load(f)

        self.movies_by_id = {m['id']: m for m in self.movies}
        self.movies_by_title = {f"{m['title']} ({m['year']})": m for m in self.movies}

        self._build_genre_index()

    def _build_genre_index(self):
        self.genre_to_movies = {}
        for movie in self.movies:
            for genre in movie['genres']:
                if genre not in self.genre_to_movies:
                    self.genre_to_movies[genre] = []
                self.genre_to_movies[genre].append(movie)

    def get_catalog(self):
        return self.movies

    def get_popular_movies(self, n=50):
        sorted_movies = sorted(self.movies, key=lambda x: x['votes'], reverse=True)
        return sorted_movies[:n]

    def recommend_from_likes(self, liked_titles: list[str], n: int = 10) -> list[dict]:
        liked_movies = []
        for title in liked_titles:
            if title in self.movies_by_title:
                liked_movies.append(self.movies_by_title[title])
            else:
                for m in self.movies:
                    if m['title'].lower() in title.lower() or title.lower() in m['title'].lower():
                        liked_movies.append(m)
                        break

        if not liked_movies:
            return []

        liked_ids = {m['id'] for m in liked_movies}
        liked_genres = []
        for m in liked_movies:
            liked_genres.extend(m['genres'])
        genre_counts = Counter(liked_genres)

        candidates = []
        for movie in self.movies:
            if movie['id'] in liked_ids:
                continue

            score = 0
            shared_genres = []
            for genre in movie['genres']:
                if genre in genre_counts:
                    score += genre_counts[genre]
                    shared_genres.append(genre)

            if score > 0:
                genre_score = score / sum(genre_counts.values())
                rating_boost = (movie['rating'] - 6) / 4
                popularity_boost = min(movie['votes'] / 1000000, 0.3)
                final_score = genre_score * 0.6 + rating_boost * 0.25 + popularity_boost * 0.15

                source_movie = self._find_best_match(movie, liked_movies)
                explanation = self._build_explanation(source_movie, shared_genres, movie['rating'])

                candidates.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'full_title': f"{movie['title']} ({movie['year']})",
                    'year': movie['year'],
                    'genres': movie['genres'],
                    'rating': movie['rating'],
                    'score': round(final_score, 2),
                    'explanation': explanation,
                    'shared_genres': shared_genres
                })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:n]

    def _find_best_match(self, target, liked_movies):
        best_match = liked_movies[0]
        best_overlap = 0
        target_genres = set(target['genres'])

        for movie in liked_movies:
            overlap = len(set(movie['genres']) & target_genres)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = movie

        return best_match

    def _build_explanation(self, source_movie, shared_genres, rating):
        parts = []

        if shared_genres:
            genres_str = ', '.join(shared_genres[:3])
            parts.append(f"Because you liked {source_movie['title']} — shares genres: {genres_str}")

        if rating >= 8.0:
            parts.append(f"Highly rated ({rating}/10)")
        elif rating >= 7.5:
            parts.append(f"Well received ({rating}/10)")

        return '. '.join(parts) if parts else "Recommended based on your taste"

    def get_similar_movies(self, title: str, n: int = 10) -> list[dict]:
        source = None
        if title in self.movies_by_title:
            source = self.movies_by_title[title]
        else:
            for m in self.movies:
                if m['title'].lower() in title.lower() or title.lower() in m['title'].lower():
                    source = m
                    break

        if not source:
            return []

        source_genres = set(source['genres'])
        candidates = []

        for movie in self.movies:
            if movie['id'] == source['id']:
                continue

            movie_genres = set(movie['genres'])
            shared = source_genres & movie_genres

            if shared:
                score = len(shared) / len(source_genres | movie_genres)
                rating_boost = (movie['rating'] - 6) / 40
                final_score = score + rating_boost

                candidates.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'full_title': f"{movie['title']} ({movie['year']})",
                    'year': movie['year'],
                    'genres': movie['genres'],
                    'rating': movie['rating'],
                    'score': round(final_score, 2),
                    'shared_genres': list(shared),
                    'explanation': f"Similar to {source['title']} — shares genres: {', '.join(shared)}"
                })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:n]


if __name__ == '__main__':
    rec = MovieRecommender()

    print('=' * 60)
    print('POPULAR MOVIES')
    print('=' * 60)
    for m in rec.get_popular_movies(5):
        print(f"  {m['title']} ({m['year']}) - {m['rating']}/10")

    print('\n' + '=' * 60)
    print('RECOMMENDATIONS')
    print('=' * 60)
    liked = ['Inception (2010)', 'The Dark Knight (2008)', 'Interstellar (2014)']
    print(f"Liked: {liked}\n")

    for r in rec.recommend_from_likes(liked, n=5):
        print(f"{r['title']} ({r['year']})")
        print(f"  Score: {r['score']} | Rating: {r['rating']}/10")
        print(f"  Why: {r['explanation']}\n")
