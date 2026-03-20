import argparse

from data_loader import load_all_data
from content_based import ContentBasedRecommender
from hybrid import HybridRecommender
from evaluate import run_evaluation


def recommend_for_user(user_id: int, n: int = 10):
    movies, ratings = load_all_data()
    recommender = HybridRecommender(movies, ratings)

    user_favs = recommender._get_user_favorites(user_id)
    if user_favs:
        print(f"\nYour top rated movies:")
        for title, rating in user_favs[:3]:
            print(f"  ★ {title} ({rating}/5)")
        print()

    recs = recommender.get_recommendations(user_id, n=n)
    if not recs:
        print(f"No recommendations found for user {user_id}")
        return

    print(f"Top {len(recs)} recommendations for you:\n")
    print("-" * 70)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Genres: {rec['genres']}")
        print(f"   Score: {rec['score']} | Predicted rating: {rec['predicted_rating']}/5")
        print(f"   Why: {rec['explanation']}")
    print()


def similar_movies(title: str, n: int = 10):
    movies, _ = load_all_data()
    recommender = ContentBasedRecommender(movies)

    recs = recommender.get_similar_movies(title, n=n)
    if not recs:
        print(f"No matches found for '{title}'")
        return

    print(f"\nMovies similar to: {title}\n")
    print("-" * 70)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Genres: {rec['genres']}")
        print(f"   Similarity: {rec['score']}")
        print(f"   {rec['explanation']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Explainable Movie Recommender',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--user', type=int, help='Get recommendations for a user ID')
    parser.add_argument('--movie', type=str, help='Find movies similar to this title')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation metrics')
    parser.add_argument('-n', type=int, default=10, help='Number of recommendations (default: 10)')

    args = parser.parse_args()

    if args.evaluate:
        run_evaluation()
    elif args.user:
        recommend_for_user(args.user, args.n)
    elif args.movie:
        similar_movies(args.movie, args.n)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
