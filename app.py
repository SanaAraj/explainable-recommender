import streamlit as st
from data_loader import load_all_data
from content_based import ContentBasedRecommender
from hybrid import HybridRecommender

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .stButton > button {
        border-radius: 8px;
    }
    .movie-card {
        background: #1e1e2e;
        border: 2px solid #333;
        border-radius: 12px;
        padding: 12px;
        min-height: 140px;
        transition: all 0.2s;
    }
    .movie-card:hover {
        border-color: #6366f1;
    }
    .movie-card.selected {
        border-color: #22c55e;
        background: #1a2e1a;
    }
    .genre-pill {
        background: #374151;
        color: #d1d5db;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-right: 4px;
        display: inline-block;
    }
    .year-badge {
        color: #9ca3af;
        font-size: 13px;
    }
    .rating-badge {
        color: #fbbf24;
        font-size: 13px;
    }
    .filter-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        cursor: pointer;
        margin: 3px;
        border: 1px solid #4b5563;
        background: transparent;
        color: #d1d5db;
    }
    .filter-pill.active {
        background: #6366f1;
        border-color: #6366f1;
        color: white;
    }
    .explanation-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-left: 4px solid #8b5cf6;
        padding: 16px;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
    }
    .explanation-label {
        color: #a78bfa;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .explanation-text {
        color: #e0e7ff;
        font-size: 15px;
        line-height: 1.5;
    }
    .match-bar {
        height: 6px;
        border-radius: 3px;
        background: #374151;
        overflow: hidden;
    }
    .match-fill {
        height: 100%;
        border-radius: 3px;
    }
    .picks-summary {
        background: #1f2937;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_recommenders():
    movies, ratings = load_all_data()
    content_rec = ContentBasedRecommender(movies)
    hybrid_rec = HybridRecommender(movies, ratings)
    popular = hybrid_rec.get_popular_movies(n=50)
    return movies, content_rec, hybrid_rec, popular


movies_df, content_rec, hybrid_rec, all_popular = load_recommenders()

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

        # Sort options
        sort_col1, sort_col2, sort_col3, sort_col4 = st.columns([1, 1, 1, 3])
        with sort_col1:
            sort_newest = st.button("Newest", type="primary" if st.session_state.get('sort_by', 'newest') == 'newest' else "secondary", use_container_width=True)
        with sort_col2:
            sort_popular = st.button("Most Popular", type="primary" if st.session_state.get('sort_by') == 'popular' else "secondary", use_container_width=True)
        with sort_col3:
            sort_rated = st.button("Highest Rated", type="primary" if st.session_state.get('sort_by') == 'rated' else "secondary", use_container_width=True)

        if sort_newest:
            st.session_state.sort_by = 'newest'
            st.rerun()
        if sort_popular:
            st.session_state.sort_by = 'popular'
            st.rerun()
        if sort_rated:
            st.session_state.sort_by = 'rated'
            st.rerun()

        # Decade filter
        st.markdown("**Decade:**")
        decade_cols = st.columns(6)
        decades = ['All', '2010s', '2000s', '1990s', '1980s', 'Earlier']
        current_decade = st.session_state.get('decade_filter', 'All')

        for i, decade in enumerate(decades):
            with decade_cols[i]:
                if st.button(decade, key=f"decade_{decade}",
                            type="primary" if current_decade == decade else "secondary",
                            use_container_width=True):
                    st.session_state.decade_filter = decade
                    st.rerun()

        # Genre filter
        st.markdown("**Genre:**")
        genre_cols = st.columns(9)
        genres = ['All', 'Action', 'Comedy', 'Drama', 'Sci-Fi', 'Thriller', 'Animation', 'Romance', 'Horror']
        current_genre = st.session_state.get('genre_filter', 'All')

        for i, genre in enumerate(genres):
            with genre_cols[i]:
                if st.button(genre, key=f"genre_{genre}",
                            type="primary" if current_genre == genre else "secondary",
                            use_container_width=True):
                    st.session_state.genre_filter = genre
                    st.rerun()

        # Search bar
        search_query = st.text_input("Search movies...", key="search", placeholder="Type to filter...")

        st.markdown("---")

        # Filter and sort movies
        filtered_movies = all_popular.copy()

        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            filtered_movies = [m for m in filtered_movies if search_lower in m['title'].lower()]

        # Apply decade filter
        if current_decade != 'All':
            if current_decade == '2010s':
                filtered_movies = [m for m in filtered_movies if 2010 <= m['year'] <= 2019]
            elif current_decade == '2000s':
                filtered_movies = [m for m in filtered_movies if 2000 <= m['year'] <= 2009]
            elif current_decade == '1990s':
                filtered_movies = [m for m in filtered_movies if 1990 <= m['year'] <= 1999]
            elif current_decade == '1980s':
                filtered_movies = [m for m in filtered_movies if 1980 <= m['year'] <= 1989]
            elif current_decade == 'Earlier':
                filtered_movies = [m for m in filtered_movies if m['year'] < 1980]

        # Apply genre filter
        if current_genre != 'All':
            filtered_movies = [m for m in filtered_movies if current_genre in m['genres']]

        # Apply sorting
        sort_by = st.session_state.get('sort_by', 'newest')
        if sort_by == 'newest':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['year'], reverse=True)
        elif sort_by == 'popular':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['num_ratings'], reverse=True)
        elif sort_by == 'rated':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['avg_rating'], reverse=True)

        # Show selected count
        n_selected = len(st.session_state.selected_movies)
        if n_selected > 0:
            selected_titles = list(st.session_state.selected_movies)[:3]
            more = f" +{n_selected - 3} more" if n_selected > 3 else ""
            st.markdown(f"**Selected ({n_selected}):** {', '.join(selected_titles)}{more}")

        # Movie grid
        if not filtered_movies:
            st.warning("No movies match your filters. Try adjusting your search or filters.")
        else:
            cols = st.columns(4)
            for idx, movie in enumerate(filtered_movies):
                col = cols[idx % 4]
                with col:
                    is_selected = movie['full_title'] in st.session_state.selected_movies
                    genres_display = ' • '.join(movie['genres'][:3])

                    btn_label = f"{'✓ ' if is_selected else ''}{movie['title']}\n{movie['year']} • ★{movie['avg_rating']}\n{genres_display[:30]}"

                    if st.button(btn_label, key=f"movie_{movie['movieId']}",
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"):
                        if is_selected:
                            st.session_state.selected_movies.discard(movie['full_title'])
                        else:
                            st.session_state.selected_movies.add(movie['full_title'])
                        st.rerun()

        st.markdown("---")

        # Get recommendations button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if n_selected >= 3:
                if st.button(f"Get Recommendations", type="primary", use_container_width=True):
                    st.session_state.show_results = True
                    st.rerun()
            else:
                st.button(f"Select {3 - n_selected} more", disabled=True, use_container_width=True)

    else:
        # Results page
        liked = list(st.session_state.selected_movies)

        # Your picks summary
        st.markdown(f"""
        <div class="picks-summary">
            <strong>Based on your picks:</strong> {', '.join(liked)}
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Recommended for you")

        with st.spinner("Finding perfect matches..."):
            recs = hybrid_rec.recommend_from_likes(liked, n=10)

        for i, rec in enumerate(recs, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Parse title and year
                    title, year = hybrid_rec._parse_title_year(rec['title'])
                    st.markdown(f"### {i}. {title}")
                    st.markdown(f"<span class='year-badge'>{year}</span>", unsafe_allow_html=True)

                    # Genre pills
                    genres = rec['genres'].split('|') if isinstance(rec['genres'], str) else rec['genres']
                    genre_html = ' '.join([f'`{g}`' for g in genres[:4]])
                    st.markdown(genre_html)

                    # Explanation box
                    st.markdown(f"""
                    <div class="explanation-box">
                        <div class="explanation-label">Why this movie?</div>
                        <div class="explanation-text">{rec['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    # Match score with color
                    score_pct = int(rec['score'] * 100)
                    if score_pct >= 50:
                        color = "#22c55e"
                    elif score_pct >= 30:
                        color = "#f59e0b"
                    else:
                        color = "#6b7280"

                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px;">
                        <div style="font-size: 28px; font-weight: bold; color: {color};">{score_pct}%</div>
                        <div style="font-size: 12px; color: #9ca3af;">Match</div>
                        <div class="match-bar" style="margin-top: 8px;">
                            <div class="match-fill" style="width: {score_pct}%; background: {color};"></div>
                        </div>
                        <div style="margin-top: 12px; font-size: 18px; color: #fbbf24;">★ {rec['avg_rating']}</div>
                        <div style="font-size: 11px; color: #9ca3af;">Avg rating</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Start Over", use_container_width=True):
                st.session_state.selected_movies = set()
                st.session_state.show_results = False
                st.rerun()

with tab2:
    st.subheader("Find movies similar to one you love")

    movie_titles = sorted(movies_df['title'].tolist())
    selected_movie = st.selectbox(
        "Type or select a movie",
        movie_titles,
        index=movie_titles.index("Inception (2010)") if "Inception (2010)" in movie_titles else 0
    )

    if st.button("Find Similar Movies", key="similar_btn", type="primary"):
        with st.spinner("Finding similar movies..."):
            recs = content_rec.get_similar_movies(selected_movie, n=10)

            title, year = hybrid_rec._parse_title_year(selected_movie)
            st.markdown(f"### Movies similar to *{title}* ({year})")
            st.markdown("---")

            for i, rec in enumerate(recs, 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        rec_title, rec_year = hybrid_rec._parse_title_year(rec['title'])
                        st.markdown(f"### {i}. {rec_title}")
                        st.markdown(f"<span class='year-badge'>{rec_year}</span>", unsafe_allow_html=True)

                        genres = rec['genres'].split('|')
                        genre_html = ' '.join([f'`{g}`' for g in genres[:4]])
                        st.markdown(genre_html)

                        st.markdown(f"""
                        <div class="explanation-box">
                            <div class="explanation-label">Why similar?</div>
                            <div class="explanation-text">{rec['explanation']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        sim_pct = int(rec['score'] * 100)
                        if sim_pct >= 50:
                            color = "#22c55e"
                        elif sim_pct >= 30:
                            color = "#f59e0b"
                        else:
                            color = "#6b7280"

                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px;">
                            <div style="font-size: 28px; font-weight: bold; color: {color};">{sim_pct}%</div>
                            <div style="font-size: 12px; color: #9ca3af;">Similar</div>
                            <div class="match-bar" style="margin-top: 8px;">
                                <div class="match-fill" style="width: {sim_pct}%; background: {color};"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")
