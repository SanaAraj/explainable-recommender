import argparse

from data_loader import load_all_data
from content_based import ContentBasedRecommender
from hybrid import HybridRecommender
from evaluate import run_evaluation


def recommend_from_likes(liked_movies: list[str], n: int = 10):
    movies, ratings = load_all_data()
    recommender = HybridRecommender(movies, ratings)

    print(f"\nMovies you like:")
    for title in liked_movies:
        print(f"  ★ {title}")
    print()

    recs = recommender.recommend_from_likes(liked_movies, n=n)
    if not recs:
        print("No recommendations found. Try different movies.")
        return

    print(f"Top {len(recs)} recommendations for you:\n")
    print("-" * 70)
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Genres: {rec['genres']}")
        print(f"   Match: {int(rec['score'] * 100)}% | Rating: {rec['avg_rating']}/5")
        print(f"   Why: {rec['explanation']}")
    print()


def show_popular(n: int = 20):
    movies, ratings = load_all_data()
    recommender = HybridRecommender(movies, ratings)

    print(f"\nPopular movies (most rated):\n")
    print("-" * 70)
    popular = recommender.get_popular_movies(n=n)
    for i, movie in enumerate(popular, 1):
        print(f"{i:2}. {movie['title']}")
        print(f"    {movie['genres'].replace('|', ', ')} | {movie['rating_count']} ratings | avg {movie['avg_rating']}/5")
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
        print(f"   Similarity: {int(rec['score'] * 100)}%")
        print(f"   {rec['explanation']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Explainable Movie Recommender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --like "Toy Story (1995)" "The Matrix (1999)" "Inception (2010)"
  python main.py --similar "The Dark Knight (2008)"
  python main.py --popular
  python main.py --evaluate
        '''
    )
    parser.add_argument('--like', nargs='+', metavar='MOVIE',
                        help='Movies you like (at least 2). Get personalized recommendations.')
    parser.add_argument('--similar', type=str, metavar='MOVIE',
                        help='Find movies similar to this title')
    parser.add_argument('--popular', action='store_true',
                        help='Show popular movies to help you pick')
    parser.add_argument('--evaluate', action='store_true',
                        help='Run evaluation metrics')
    parser.add_argument('-n', type=int, default=10,
                        help='Number of results (default: 10)')

    args = parser.parse_args()

    if args.evaluate:
        run_evaluation()
    elif args.like:
        if len(args.like) < 2:
            print("Please specify at least 2 movies you like.")
            return
        recommend_from_likes(args.like, args.n)
    elif args.similar:
        similar_movies(args.similar, args.n)
    elif args.popular:
        show_popular(args.n)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
