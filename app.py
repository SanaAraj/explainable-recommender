import streamlit as st
from recommender import MovieRecommender

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .stButton > button { border-radius: 8px; }
    .genre-pill {
        background: #374151;
        color: #d1d5db;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-right: 4px;
        display: inline-block;
    }
    .year-badge { color: #9ca3af; font-size: 13px; }
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
    .explanation-text { color: #e0e7ff; font-size: 15px; line-height: 1.5; }
    .match-bar { height: 6px; border-radius: 3px; background: #374151; overflow: hidden; }
    .match-fill { height: 100%; border-radius: 3px; }
    .picks-summary {
        background: #1f2937;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()
all_movies = rec.get_catalog()

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
        sort_col1, sort_col2, sort_col3, _ = st.columns([1, 1, 1, 3])
        with sort_col1:
            if st.button("Newest", type="primary" if st.session_state.get('sort_by', 'newest') == 'newest' else "secondary", use_container_width=True):
                st.session_state.sort_by = 'newest'
                st.rerun()
        with sort_col2:
            if st.button("Most Popular", type="primary" if st.session_state.get('sort_by') == 'popular' else "secondary", use_container_width=True):
                st.session_state.sort_by = 'popular'
                st.rerun()
        with sort_col3:
            if st.button("Highest Rated", type="primary" if st.session_state.get('sort_by') == 'rated' else "secondary", use_container_width=True):
                st.session_state.sort_by = 'rated'
                st.rerun()

        # Decade filter
        st.markdown("**Decade:**")
        decade_cols = st.columns(6)
        decades = ['All', '2020s', '2010s', '2000s', '1990s', 'Earlier']
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
        filtered_movies = all_movies.copy()

        if search_query:
            search_lower = search_query.lower()
            filtered_movies = [m for m in filtered_movies if search_lower in m['title'].lower()]

        if current_decade != 'All':
            if current_decade == '2020s':
                filtered_movies = [m for m in filtered_movies if 2020 <= m['year'] <= 2029]
            elif current_decade == '2010s':
                filtered_movies = [m for m in filtered_movies if 2010 <= m['year'] <= 2019]
            elif current_decade == '2000s':
                filtered_movies = [m for m in filtered_movies if 2000 <= m['year'] <= 2009]
            elif current_decade == '1990s':
                filtered_movies = [m for m in filtered_movies if 1990 <= m['year'] <= 1999]
            elif current_decade == 'Earlier':
                filtered_movies = [m for m in filtered_movies if m['year'] < 1990]

        if current_genre != 'All':
            filtered_movies = [m for m in filtered_movies if current_genre in m['genres']]

        sort_by = st.session_state.get('sort_by', 'newest')
        if sort_by == 'newest':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['year'], reverse=True)
        elif sort_by == 'popular':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['votes'], reverse=True)
        elif sort_by == 'rated':
            filtered_movies = sorted(filtered_movies, key=lambda x: x['rating'], reverse=True)

        # Show selected count
        n_selected = len(st.session_state.selected_movies)
        if n_selected > 0:
            selected_list = list(st.session_state.selected_movies)[:3]
            more = f" +{n_selected - 3} more" if n_selected > 3 else ""
            st.markdown(f"**Selected ({n_selected}):** {', '.join(selected_list)}{more}")

        # Movie grid
        if not filtered_movies:
            st.warning("No movies match your filters. Try adjusting your search or filters.")
        else:
            cols = st.columns(4)
            for idx, movie in enumerate(filtered_movies):
                col = cols[idx % 4]
                full_title = f"{movie['title']} ({movie['year']})"
                with col:
                    is_selected = full_title in st.session_state.selected_movies
                    genres_display = ' • '.join(movie['genres'][:3])

                    btn_label = f"{'✓ ' if is_selected else ''}{movie['title']}\n{movie['year']} • ★{movie['rating']}\n{genres_display[:30]}"

                    if st.button(btn_label, key=f"movie_{movie['id']}",
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"):
                        if is_selected:
                            st.session_state.selected_movies.discard(full_title)
                        else:
                            st.session_state.selected_movies.add(full_title)
                        st.rerun()

        st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if n_selected >= 3:
                if st.button("Get Recommendations", type="primary", use_container_width=True):
                    st.session_state.show_results = True
                    st.rerun()
            else:
                st.button(f"Select {3 - n_selected} more", disabled=True, use_container_width=True)

    else:
        liked = list(st.session_state.selected_movies)

        st.markdown(f"""
        <div class="picks-summary">
            <strong>Based on your picks:</strong> {', '.join(liked)}
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Recommended for you")

        with st.spinner("Finding perfect matches..."):
            recs = rec.recommend_from_likes(liked, n=10)

        for i, r in enumerate(recs, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### {i}. {r['title']}")
                    st.markdown(f"<span class='year-badge'>{r['year']}</span>", unsafe_allow_html=True)

                    genre_html = ' '.join([f'`{g}`' for g in r['genres'][:4]])
                    st.markdown(genre_html)

                    st.markdown(f"""
                    <div class="explanation-box">
                        <div class="explanation-label">Why this movie?</div>
                        <div class="explanation-text">{r['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    score_pct = int(r['score'] * 100)
                    color = "#22c55e" if score_pct >= 50 else "#f59e0b" if score_pct >= 30 else "#6b7280"

                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px;">
                        <div style="font-size: 28px; font-weight: bold; color: {color};">{score_pct}%</div>
                        <div style="font-size: 12px; color: #9ca3af;">Match</div>
                        <div class="match-bar" style="margin-top: 8px;">
                            <div class="match-fill" style="width: {score_pct}%; background: {color};"></div>
                        </div>
                        <div style="margin-top: 12px; font-size: 18px; color: #fbbf24;">★ {r['rating']}/10</div>
                        <div style="font-size: 11px; color: #9ca3af;">Rating</div>
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

    movie_titles = sorted([f"{m['title']} ({m['year']})" for m in all_movies])
    selected_movie = st.selectbox("Type or select a movie", movie_titles, index=0)

    if st.button("Find Similar Movies", key="similar_btn", type="primary"):
        with st.spinner("Finding similar movies..."):
            recs = rec.get_similar_movies(selected_movie, n=10)

            if recs:
                st.markdown(f"### Movies similar to *{selected_movie}*")
                st.markdown("---")

                for i, r in enumerate(recs, 1):
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"### {i}. {r['title']}")
                            st.markdown(f"<span class='year-badge'>{r['year']}</span>", unsafe_allow_html=True)

                            genre_html = ' '.join([f'`{g}`' for g in r['genres'][:4]])
                            st.markdown(genre_html)

                            st.markdown(f"""
                            <div class="explanation-box">
                                <div class="explanation-label">Why similar?</div>
                                <div class="explanation-text">{r['explanation']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            sim_pct = int(r['score'] * 100)
                            color = "#22c55e" if sim_pct >= 50 else "#f59e0b" if sim_pct >= 30 else "#6b7280"

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
            else:
                st.warning("No similar movies found.")
