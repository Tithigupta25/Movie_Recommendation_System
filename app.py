import streamlit as st
import pickle
import pandas as pd
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer



# Function to fetch movie poster using TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=beca8e1268f3ce6a031650cd615715a7"
    
    for _ in range(3):  # Retry up to 3 times silently
        try:
            response = requests.get(url, timeout=10, verify=True)
            response.raise_for_status()
            data = response.json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w185/" + data['poster_path']
            else:
                return "https://via.placeholder.com/185x278?text=No+Image"
        except requests.exceptions.SSLError:
            time.sleep(1)
        except requests.exceptions.RequestException:
            time.sleep(1)
    
    # Return placeholder if all attempts fail
    return "https://via.placeholder.com/185x278?text=No+Image"


# Function to recommend movies
def recommend(movie):
    try:
        # Find the movie index from the dataset
        movie_index = movies[movies["title"] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_posters = []

        # Fetch posters for the top 5 similar movies
        for i in movie_list:
            movie_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_posters

    except IndexError:
        st.error(f"Movie '{movie}' not found in the dataset.")
        return [], []
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []


# Load movie data and similarity matrix
try:
    movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movie_dict)
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies['tag']).toarray()
    similarity = cosine_similarity(vectors)
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()


# Streamlit UI
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox('Select a Movie', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    if names and posters:
        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.image(poster)
                st.caption(name)
    else:
        st.warning("No recommendations available.")
