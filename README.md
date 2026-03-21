# Explainable Recommender

A movie recommendation system that tells you *why* it recommends each movie.

## What it does

Pick movies you like, get recommendations with clear explanations. The recommender analyzes genres, ratings, and movie similarities to find films you'll love — and tells you exactly why each one was picked.

## Features

- **150 curated popular movies** from 1993–2024 (Oppenheimer, Barbie, Dune, and classics)
- **No API keys needed** — works out of the box
- **Sort** by newest, most popular, or highest rated
- **Filter** by decade (2020s, 2010s, 2000s, 1990s) and genre
- **Search** to quickly find specific movies
- **Explanations** for every recommendation

## Example output

```
Movies you like:
  ★ Inception (2010)
  ★ The Dark Knight (2008)
  ★ Interstellar (2014)

Top 5 recommendations for you:

1. Dune: Part Two (2024)
   Genres: Sci-Fi, Adventure, Drama
   Match: 61% | Rating: 8.6/10
   Why: Because you liked Interstellar — shares genres: Sci-Fi, Adventure, Drama. Highly rated (8.6/10)

2. The Lord of the Rings: The Return of the King (2003)
   Genres: Action, Adventure, Drama
   Match: 63% | Rating: 9.0/10
   Why: Because you liked Inception — shares genres: Action, Adventure, Drama. Highly rated (9.0/10)
```

## Web UI

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 — pick movies from a grid, get recommendations with explanations.

## CLI Usage

Get recommendations based on movies you like:
```bash
python main.py --like "Inception (2010)" "The Dark Knight (2008)" "Interstellar (2014)"
```

Find similar movies:
```bash
python main.py --similar "Pulp Fiction (1994)"
```

See popular movies:
```bash
python main.py --popular
```

## Setup

```bash
git clone https://github.com/SanaAraj/explainable-recommender.git
cd explainable-recommender
pip install -r requirements.txt
```

## How it works

1. **Genre matching** — finds movies that share genres with your picks
2. **Rating boost** — prioritizes highly-rated films
3. **Popularity signal** — considers how many people rated the movie
4. **Explanations** — tells you which of your picks caused each recommendation and why

## Tech stack

- Python 3.10+
- Streamlit (web UI)
- No external APIs required
