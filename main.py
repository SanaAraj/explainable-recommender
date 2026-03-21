import argparse
from recommender import MovieRecommender


def recommend_from_likes(liked_movies: list[str], n: int = 10):
    rec = MovieRecommender()

    print(f"\nMovies you like:")
    for title in liked_movies:
        print(f"  ★ {title}")
    print()

    recs = rec.recommend_from_likes(liked_movies, n=n)
    if not recs:
        print("No recommendations found. Try different movies.")
        return

    print(f"Top {len(recs)} recommendations for you:\n")
    print("-" * 70)
    for i, r in enumerate(recs, 1):
        print(f"\n{i}. {r['title']} ({r['year']})")
        print(f"   Genres: {', '.join(r['genres'])}")
        print(f"   Match: {int(r['score'] * 100)}% | Rating: {r['rating']}/10")
        print(f"   Why: {r['explanation']}")
    print()


def show_popular(n: int = 20):
    rec = MovieRecommender()

    print(f"\nPopular movies:\n")
    print("-" * 70)
    for i, m in enumerate(rec.get_popular_movies(n), 1):
        print(f"{i:2}. {m['title']} ({m['year']})")
        print(f"    {', '.join(m['genres'])} | Rating: {m['rating']}/10")
    print()


def similar_movies(title: str, n: int = 10):
    rec = MovieRecommender()

    recs = rec.get_similar_movies(title, n=n)
    if not recs:
        print(f"No matches found for '{title}'")
        return

    print(f"\nMovies similar to: {title}\n")
    print("-" * 70)
    for i, r in enumerate(recs, 1):
        print(f"\n{i}. {r['title']} ({r['year']})")
        print(f"   Genres: {', '.join(r['genres'])}")
        print(f"   Similarity: {int(r['score'] * 100)}%")
        print(f"   {r['explanation']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Explainable Movie Recommender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --like "Inception (2010)" "The Dark Knight (2008)" "Interstellar (2014)"
  python main.py --similar "Pulp Fiction (1994)"
  python main.py --popular
        '''
    )
    parser.add_argument('--like', nargs='+', metavar='MOVIE',
                        help='Movies you like (at least 2). Get personalized recommendations.')
    parser.add_argument('--similar', type=str, metavar='MOVIE',
                        help='Find movies similar to this title')
    parser.add_argument('--popular', action='store_true',
                        help='Show popular movies')
    parser.add_argument('-n', type=int, default=10,
                        help='Number of results (default: 10)')

    args = parser.parse_args()

    if args.like:
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
