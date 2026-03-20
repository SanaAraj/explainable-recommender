import streamlit as st
from data_loader import load_all_data
from content_based import ContentBasedRecommender
from hybrid import HybridRecommender

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .movie-card {
        border: 2px solid #333;
        border-radius: 10px;
        padding: 12px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.2s;
        background: #1a1a2e;
        min-height: 120px;
    }
    .movie-card:hover {
        border-color: #6366f1;
    }
    .movie-card.selected {
        border-color: #6366f1;
        background: #1e1e3f;
    }
    .movie-title {
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 5px;
        color: #fff;
    }
    .movie-genres {
        font-size: 11px;
        color: #888;
    }
    .genre-pill {
        background: #333;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        margin-right: 4px;
        display: inline-block;
        margin-bottom: 3px;
    }
    .explanation-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 4px solid #6366f1;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .rec-title {
        font-size: 18px;
        font-weight: 600;
        color: #fff;
    }
    .score-bar {
        background: #333;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }
    .score-fill {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        height: 100%;
    }
    .big-button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_recommenders():
    movies, ratings = load_all_data()
    content_rec = ContentBasedRecommender(movies)
    hybrid_rec = HybridRecommender(movies, ratings)
    return movies, content_rec, hybrid_rec


movies, content_rec, hybrid_rec = load_recommenders()

if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = set()
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

st.title("Movie Recommender")
st.markdown("*Pick movies you love. We'll explain why you'll love these too.*")

tab1, tab2 = st.tabs(["For You", "Similar Movies"])

with tab1:
    if not st.session_state.show_results:
        st.subheader("Select at least 3 movies you enjoy")

        popular = hybrid_rec.get_popular_movies(n=30)

        cols = st.columns(4)
        for idx, movie in enumerate(popular):
            col = cols[idx % 4]
            with col:
                is_selected = movie['title'] in st.session_state.selected_movies

                genres = movie['genres'].replace('|', ' • ')

                if st.button(
                    f"{'✓ ' if is_selected else ''}{movie['title']}\n{genres[:40]}",
                    key=f"movie_{movie['movieId']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    if is_selected:
                        st.session_state.selected_movies.discard(movie['title'])
                    else:
                        st.session_state.selected_movies.add(movie['title'])
                    st.rerun()

        st.markdown("---")

        n_selected = len(st.session_state.selected_movies)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if n_selected >= 3:
                if st.button(f"Get Recommendations ({n_selected} selected)", type="primary", use_container_width=True):
                    st.session_state.show_results = True
                    st.rerun()
            else:
                st.button(f"Select {3 - n_selected} more movie{'s' if 3 - n_selected > 1 else ''}", disabled=True, use_container_width=True)

    else:
        liked = list(st.session_state.selected_movies)

        st.subheader("Your picks")
        cols = st.columns(min(len(liked), 5))
        for i, title in enumerate(liked[:5]):
            with cols[i]:
                st.success(f"✓ {title[:25]}...")

        st.markdown("---")
        st.subheader("Recommended for you")

        with st.spinner("Finding perfect matches..."):
            recs = hybrid_rec.recommend_from_likes(liked, n=10)

        for i, rec in enumerate(recs, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {i}. {rec['title']}")

                    genres = rec['genres'].split('|')
                    genre_html = ' '.join([f'`{g}`' for g in genres])
                    st.markdown(genre_html)

                    st.markdown(f"""
                    <div class="explanation-box">
                        <strong>Why this movie?</strong><br/>
                        {rec['explanation']}
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    score_pct = int(rec['score'] * 100)
                    st.metric("Match", f"{score_pct}%")
                    st.metric("Rating", f"⭐ {rec['avg_rating']}/5")

                st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Start Over", use_container_width=True):
                st.session_state.selected_movies = set()
                st.session_state.show_results = False
                st.rerun()

with tab2:
    st.subheader("Find movies similar to one you love")

    movie_titles = sorted(movies['title'].tolist())
    selected_movie = st.selectbox(
        "Type or select a movie",
        movie_titles,
        index=movie_titles.index("Inception (2010)") if "Inception (2010)" in movie_titles else 0
    )

    if st.button("Find Similar Movies", key="similar_btn", type="primary"):
        with st.spinner("Finding similar movies..."):
            recs = content_rec.get_similar_movies(selected_movie, n=10)

            st.markdown(f"### Movies similar to *{selected_movie}*")
            st.markdown("---")

            for i, rec in enumerate(recs, 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"### {i}. {rec['title']}")

                        genres = rec['genres'].split('|')
                        genre_html = ' '.join([f'`{g}`' for g in genres])
                        st.markdown(genre_html)

                        st.markdown(f"""
                        <div class="explanation-box">
                            {rec['explanation']}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        sim_pct = int(rec['score'] * 100)
                        st.metric("Similarity", f"{sim_pct}%")

                    st.markdown("---")
