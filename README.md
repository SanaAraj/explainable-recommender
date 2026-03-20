# Explainable Recommender

A movie recommendation system that tells you *why* it recommends each movie.

## What it does

This hybrid recommender combines content-based filtering (movie genres/tags) with collaborative filtering (user rating patterns) to generate personalized movie recommendations. The key feature is explainability: every recommendation comes with a human-readable explanation of why that movie was selected for you.

## How it works

The system uses three approaches:

1. **Content-based filtering**: TF-IDF vectorization of movie genres and user-generated tags, with cosine similarity to find movies with similar content profiles.

2. **Collaborative filtering**: SVD matrix factorization on the user-item rating matrix to identify users with similar taste and predict ratings for unseen movies.

3. **Explainability layer**: For each recommendation, the system generates an explanation combining relevant signals — shared genres with movies you liked, common tags, and how similar users rated the movie.

## Example output

```
Top 5 recommendations for you:

1. Big Lebowski, The (1998)
   Genres: Comedy|Crime
   Score: 0.48 | Predicted rating: 3.7/5
   Why: Users with similar taste rated this 3.9/5

2. Mission: Impossible II (2000)
   Genres: Action|Adventure|Thriller
   Score: 0.4 | Predicted rating: 3.5/5
   Why: Similar to GoldenEye (1995) — shares genres: Action, Adventure, Thriller
        Users with similar taste rated this 2.7/5
```

## Dataset

Uses the MovieLens Small dataset (~100k ratings, 9k movies, 600 users). The dataset downloads automatically on first run.

## Setup

```bash
git clone https://github.com/SanaAraj/explainable-recommender.git
cd explainable-recommender
pip install -r requirements.txt
```

## Usage

Get personalized recommendations for a user:
```bash
python main.py --user 42
```

Find similar movies:
```bash
python main.py --movie "Toy Story"
```

Run evaluation:
```bash
python main.py --evaluate
```

Customize number of results:
```bash
python main.py --user 42 -n 20
```

## Evaluation

On a 80/20 train-test split:
- Collaborative filtering RMSE: ~3.1
- Hybrid Precision@10: ~0.14
- Hybrid Recall@10: ~0.08

## Tech stack

- Python 3.10+
- pandas, numpy
- scikit-learn (TF-IDF, cosine similarity)
- scipy (SVD)
