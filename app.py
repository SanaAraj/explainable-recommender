import streamlit as st
from data_loader import load_all_data
from content_based import ContentBasedRecommender
from hybrid import HybridRecommender

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

@st.cache_resource
def load_recommenders():
    movies, ratings = load_all_data()
    content_rec = ContentBasedRecommender(movies)
    hybrid_rec = HybridRecommender(movies, ratings)
    return movies, ratings, content_rec, hybrid_rec

movies, ratings, content_rec, hybrid_rec = load_recommenders()

st.title("Explainable Movie Recommender")
st.markdown("Get movie recommendations with clear explanations of *why* each movie was picked for you.")

tab1, tab2 = st.tabs(["Personalized Recommendations", "Similar Movies"])

with tab1:
    st.subheader("Get recommendations based on your taste")

    user_ids = sorted(ratings['userId'].unique())
    user_id = st.selectbox("Select User ID", user_ids, index=user_ids.index(42) if 42 in user_ids else 0)
    n_recs = st.slider("Number of recommendations", 5, 20, 10)

    if st.button("Get Recommendations", key="user_rec"):
        with st.spinner("Finding movies for you..."):
            user_favs = hybrid_rec._get_user_favorites(user_id)

            if user_favs:
                st.markdown("**Your top rated movies:**")
                cols = st.columns(min(len(user_favs), 3))
                for i, (title, rating) in enumerate(user_favs[:3]):
                    with cols[i]:
                        st.metric(label=title[:30] + "..." if len(title) > 30 else title, value=f"⭐ {rating}/5")

            st.markdown("---")
            recs = hybrid_rec.get_recommendations(user_id, n=n_recs)

            for i, rec in enumerate(recs, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {i}. {rec['title']}")
                        st.caption(rec['genres'])
                        st.info(f"💡 **Why:** {rec['explanation']}")
                    with col2:
                        st.metric("Score", rec['score'])
                        st.metric("Predicted", f"{rec['predicted_rating']}/5")
                    st.markdown("---")

with tab2:
    st.subheader("Find movies similar to one you love")

    movie_titles = sorted(movies['title'].tolist())
    selected_movie = st.selectbox("Select a movie", movie_titles, index=movie_titles.index("Toy Story (1995)") if "Toy Story (1995)" in movie_titles else 0)
    n_similar = st.slider("Number of similar movies", 5, 20, 10, key="similar_slider")

    if st.button("Find Similar", key="similar_rec"):
        with st.spinner("Finding similar movies..."):
            recs = content_rec.get_similar_movies(selected_movie, n=n_similar)

            for i, rec in enumerate(recs, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {i}. {rec['title']}")
                        st.caption(rec['genres'])
                        st.info(f"💡 {rec['explanation']}")
                    with col2:
                        st.metric("Similarity", rec['score'])
                    st.markdown("---")
