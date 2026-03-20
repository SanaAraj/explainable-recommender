import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from data_loader import load_all_data
from collaborative import CollaborativeRecommender
from hybrid import HybridRecommender


def rmse(predictions: list[tuple[float, float]]) -> float:
    if not predictions:
        return 0.0
    errors = [(actual - pred) ** 2 for pred, actual in predictions]
    return np.sqrt(np.mean(errors))


def precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if k == 0:
        return 0.0
    recommended_k = recommended[:k]
    hits = len(set(recommended_k) & relevant)
    return hits / k


def recall_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    recommended_k = recommended[:k]
    hits = len(set(recommended_k) & relevant)
    return hits / len(relevant)


def evaluate_collaborative(ratings: pd.DataFrame, movies: pd.DataFrame,
                           test_size: float = 0.2) -> dict:
    train, test = train_test_split(ratings, test_size=test_size, random_state=42)

    rec = CollaborativeRecommender(train, movies)

    predictions = []
    for _, row in test.iterrows():
        user_id, movie_id, actual = row['userId'], row['movieId'], row['rating']
        pred = rec.predict_rating(user_id, movie_id)
        predictions.append((pred, actual))

    return {'rmse': round(rmse(predictions), 4), 'n_predictions': len(predictions)}


def evaluate_hybrid(ratings: pd.DataFrame, movies: pd.DataFrame,
                    k: int = 10, threshold: float = 4.0, n_users: int = 100) -> dict:
    train, test = train_test_split(ratings, test_size=0.2, random_state=42)

    rec = HybridRecommender(movies, train)

    test_users = test['userId'].unique()[:n_users]
    precisions, recalls = [], []

    for user_id in test_users:
        user_test = test[(test['userId'] == user_id) & (test['rating'] >= threshold)]
        if user_test.empty:
            continue

        relevant = set(user_test['movieId'])
        recommendations = rec.get_recommendations(user_id, n=k)
        recommended_ids = [r['movieId'] for r in recommendations]

        precisions.append(precision_at_k(recommended_ids, relevant, k))
        recalls.append(recall_at_k(recommended_ids, relevant, k))

    return {
        f'precision@{k}': round(np.mean(precisions), 4) if precisions else 0,
        f'recall@{k}': round(np.mean(recalls), 4) if recalls else 0,
        'n_users_evaluated': len(precisions)
    }


def run_evaluation():
    print('Loading data...')
    movies, ratings = load_all_data()

    print('\nEvaluating collaborative filtering (RMSE)...')
    collab_results = evaluate_collaborative(ratings, movies)
    print(f"  RMSE: {collab_results['rmse']}")
    print(f"  Predictions: {collab_results['n_predictions']}")

    print('\nEvaluating hybrid recommender (Precision/Recall@10)...')
    hybrid_results = evaluate_hybrid(ratings, movies, k=10)
    print(f"  Precision@10: {hybrid_results['precision@10']}")
    print(f"  Recall@10: {hybrid_results['recall@10']}")
    print(f"  Users evaluated: {hybrid_results['n_users_evaluated']}")

    return {'collaborative': collab_results, 'hybrid': hybrid_results}


if __name__ == '__main__':
    run_evaluation()
