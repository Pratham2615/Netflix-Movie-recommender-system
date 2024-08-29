import pickle
import streamlit as st
import requests
import numpy as np

# Initialize feedback storage
if 'liked_movies' not in st.session_state:
    st.session_state.liked_movies = set()
if 'disliked_movies' not in st.session_state:
    st.session_state.disliked_movies = set()
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=67de355358e00a61ab157ffe59b4da67&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    return f"https://image.tmdb.org/t/p/w500/{poster_path}"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    overview_movie = overview[index]
    rating_movie = rating[index]
    runtime_movie=runtime[index]

    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[0:15]:  # Increase the pool of recommendations
        movie_id = movies.iloc[i[0]].movie_id
        movie_title = movies.iloc[i[0]].title
        # Avoid movies in disliked list and prefer movies in liked list
        if movie_title in st.session_state.disliked_movies:
            continue
        if len(recommended_movie_names) < 6:
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movie_title)

    return recommended_movie_names, recommended_movie_posters,overview_movie,rating_movie,runtime_movie


def handle_feedback(movie_name, liked):
    if liked:
        st.session_state.liked_movies.add(movie_name)
        if movie_name in st.session_state.disliked_movies:
            st.session_state.disliked_movies.remove(movie_name)
    else:
        st.session_state.disliked_movies.add(movie_name)
        if movie_name in st.session_state.liked_movies:
            st.session_state.liked_movies.remove(movie_name)


st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
overview= pickle.load(open('overview.pkl','rb'))
rating=pickle.load(open('rating.pkl','rb'))
runtime=pickle.load(open('runtime.pkl','rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    st.session_state.recommendations = recommend(selected_movie)

if st.session_state.recommendations:
    recommended_movie_names, recommended_movie_posters,overview_movie,rating_movie,runtime_movie = st.session_state.recommendations

    col1,col2=st.columns(2)
    with col1:
        st.image(recommended_movie_posters[0],width=275)
    with col2:
        st.header(':blue[Overview]')
        st.markdown(overview_movie)
        col3,col4,col5=st.columns(3)
        with col3:
            st.markdown('Rating :star:')
            st.markdown('Runtime(min)')
        with col4:
            st.markdown(rating_movie)
            st.markdown(runtime_movie)


    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.text(recommended_movie_names[idx+1])
            st.image(recommended_movie_posters[idx+1])
            if st.button(f"👍 Like {idx + 1}", key=f"like_{idx+1}"):
                handle_feedback(recommended_movie_names[idx+1], liked=True)
            if st.button(f"👎 Dislike {idx + 1}", key=f"dislike_{idx+1}"):
                handle_feedback(recommended_movie_names[idx+1], liked=False)

if st.button('Reload Recommendations'):
    st.session_state.recommendations = recommend(selected_movie)
    st.rerun()
