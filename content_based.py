import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data_loader import load_all_data


class ContentBasedRecommender:
    def __init__(self, movies: pd.DataFrame):
        self.movies = movies.copy()
        self.movies['content'] = self.movies['genres'].str.replace('|', ' ', regex=False) + ' ' + self.movies['tags']
        self.movies['content'] = self.movies['content'].str.lower()

        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies['content'])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

        self.title_to_idx = {title: idx for idx, title in enumerate(self.movies['title'])}
        self.idx_to_movie = self.movies.reset_index(drop=True)

    def get_similar_movies(self, title: str, n: int = 10) -> list[dict]:
        if title not in self.title_to_idx:
            matches = self.movies[self.movies['title'].str.contains(title, case=False, na=False)]
            if matches.empty:
                return []
            title = matches.iloc[0]['title']

        idx = self.title_to_idx[title]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]

        source_genres = set(self.idx_to_movie.iloc[idx]['genres'].split('|'))
        source_tags = set(self.idx_to_movie.iloc[idx]['tags'].split())

        results = []
        for movie_idx, score in sim_scores:
            movie = self.idx_to_movie.iloc[movie_idx]
            target_genres = set(movie['genres'].split('|'))
            target_tags = set(movie['tags'].split()) if movie['tags'] else set()

            shared_genres = source_genres & target_genres
            shared_tags = source_tags & target_tags

            explanation = self._build_explanation(title, shared_genres, shared_tags)

            results.append({
                'movieId': movie['movieId'],
                'title': movie['title'],
                'genres': movie['genres'],
                'score': round(score, 3),
                'explanation': explanation,
                'shared_genres': list(shared_genres),
                'shared_tags': list(shared_tags)[:5]
            })

        return results

    def _build_explanation(self, source_title: str, shared_genres: set, shared_tags: set) -> str:
        parts = []
        if shared_genres:
            parts.append(f"shares genres: {', '.join(sorted(shared_genres))}")
        if shared_tags:
            tags_preview = list(shared_tags)[:3]
            parts.append(f"common tags: {', '.join(tags_preview)}")

        if parts:
            return f"Similar to {source_title} — {'; '.join(parts)}"
        return f"Similar content profile to {source_title}"


if __name__ == '__main__':
    movies, _ = load_all_data()
    recommender = ContentBasedRecommender(movies)

    print('=' * 60)
    print('Content-based recommendations for "Toy Story (1995)"')
    print('=' * 60)

    recs = recommender.get_similar_movies('Toy Story (1995)', n=5)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']}")
        print(f"   {rec['explanation']}")
