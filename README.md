# Explainable Recommender

A movie recommendation system that tells you *why* it recommends each movie.

## What it does

Pick movies you like, get recommendations with clear explanations. This hybrid recommender combines content-based filtering (genres, tags) with collaborative filtering (what similar users enjoyed) to find movies you'll love — and tells you exactly why each one was picked.

## How it works

1. **You pick movies you like** from a grid of popular films
2. **Content matching** finds movies with similar genres and themes
3. **Collaborative filtering** finds what users with similar taste enjoyed
4. **Explanations** tell you exactly why each movie was recommended

## Example output

```
Movies you like:
  ★ Toy Story (1995)
  ★ The Matrix (1999)
  ★ Pulp Fiction (1994)

Top 5 recommendations for you:

1. Fight Club (1999)
   Genres: Action, Crime, Drama, Thriller
   Match: 56% | Rating: 4.6/5
   Why: Because you liked Pulp Fiction (1994) — shares genres: Crime, Thriller, Drama.
        Fans of your picks rated this 4.6/5

2. Toy Story 2 (1999)
   Genres: Adventure, Animation, Children, Comedy, Fantasy
   Match: 53% | Rating: 4.5/5
   Why: Because you liked Toy Story (1995) — shares genres: Adventure, Animation, Comedy.
        Fans of your picks rated this 4.5/5
```

## Web UI

Run the interactive web app:
```bash
pip install streamlit
streamlit run app.py
```

Open http://localhost:8501 to use the web interface:

- **Browse 50 popular movies** in a sortable, filterable grid
- **Sort** by newest, most popular, or highest rated
- **Filter** by decade (2010s, 2000s, 1990s, etc.) and genre (Action, Comedy, Drama, etc.)
- **Search** to quickly find specific movies
- **Select 3+ movies** you like, then get personalized recommendations
- Each recommendation includes a **clear explanation** of why it was picked

## CLI Usage

Get recommendations based on movies you like:
```bash
python main.py --like "Toy Story (1995)" "The Matrix (1999)" "Pulp Fiction (1994)"
```

Find similar movies:
```bash
python main.py --similar "The Dark Knight (2008)"
```

See popular movies (to help you pick):
```bash
python main.py --popular
```

Run evaluation:
```bash
python main.py --evaluate
```

## Dataset

Uses MovieLens Small (~100k ratings, 9k movies). Downloads automatically on first run.

## Setup

```bash
git clone https://github.com/SanaAraj/explainable-recommender.git
cd explainable-recommender
pip install -r requirements.txt
```

## Tech stack

- Python 3.10+
- pandas, numpy, scikit-learn, scipy
- Streamlit (web UI)
