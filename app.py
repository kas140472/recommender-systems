import streamlit as st
import pickle
import requests
import pandas as pd

# Load the movies and fanfic data from pickle files
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = movies_list['title'].values

# Load pre-generated recommendations for movies
recommendations = pickle.load(open('recommendations.pkl', 'rb'))

fanfics_list = pickle.load(open('fanfics.pkl', 'rb'))
fanfics = fanfics_list['title'].values

# Load pre-generated recommendations for fanfics
recommendations_fanfic = pickle.load(open('recommendations_fanfic.pkl', 'rb'))

# Function to fetch movie poster using The Movie Database (TMDb) API
def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=3100354135fbba3f21af9946689f2eca&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w185/" + data['poster_path']

# Function to recommend movies based on selected movie and number of recommendations
def recommend_movie(movie, num_recs):
    # Find the movie's recommendations in the recommendations list
    movie_recommendations = next((rec for rec in recommendations if rec['movie'] == movie), None)
    if not movie_recommendations:
        return [], [] # Return empty lists if no recommendations are found

    # Get the top movie recommendations up to the specified number
    top_recs = movie_recommendations['recommendations'][:num_recs]
    recommended_movies = [rec['title'] for rec in top_recs] # List of recommended movie titles
    recommended_movies_posters = [
        fetch_poster(movies_list[movies_list['title'] == title].movie_id.values[0]) for title in recommended_movies
    ] # List of posters for the recommended movies
    return recommended_movies, recommended_movies_posters # Return both movie titles and posters

# Function to recommend fanfics based on selected fanfic and number of recommendations
def recommend_fanfic(fanfic, num_recs):
    # Find the fanfic's recommendations in the recommendations list
    fanfic_recommendations = next((rec for rec in recommendations_fanfic if rec['fanfic'] == fanfic), None)
    if not fanfic_recommendations:
        return [], [] # Return empty lists if no recommendations are found

    # Get the top fanfic recommendations up to the specified number
    top_recs = fanfic_recommendations['recommendations'][:num_recs]
    recommended_fanfics = [rec['title'] for rec in top_recs] # List of recommended fanfic titles

    # Lists to hold details for each recommended fanfic
    recommended_fanfics_titles = []
    recommended_fanfics_genres = []
    recommended_fanfics_rating = []
    recommended_fanfics_pairing = []
    recommended_fanfics_characters = []
    recommended_fanfics_synopsis = []

    # Loop through recommended fanfics to get additional details from the fanfic list
    for title_str in recommended_fanfics:
        rec_fanfic_index = fanfics_list.loc[fanfics_list['title'] == title_str].index[0]
        recommended_fanfics_titles.append(fanfics_list.iloc[rec_fanfic_index].title)
        recommended_fanfics_genres.append(fanfics_list.iloc[rec_fanfic_index].genre)
        recommended_fanfics_rating.append(fanfics_list.iloc[rec_fanfic_index].rating)
        recommended_fanfics_pairing.append(fanfics_list.iloc[rec_fanfic_index].pairing)
        recommended_fanfics_characters.append(fanfics_list.iloc[rec_fanfic_index].characters)
        recommended_fanfics_synopsis.append(fanfics_list.iloc[rec_fanfic_index].synopsis)

    # Create a dataframe to display the fanfic recommendations with additional details
    df = pd.DataFrame({
        "title": recommended_fanfics_titles,
        "genre": recommended_fanfics_genres,
        "rating": recommended_fanfics_rating,
        "pairing": recommended_fanfics_pairing,
        "characters": recommended_fanfics_characters,
        "synopsis": recommended_fanfics_synopsis,
    })
    return df # Return the dataframe of fanfic recommendations

# Set up Streamlit title and tabs
st.title('RecsHub') # Main title for the app

tab1, tab2 = st.tabs(["Movies", "Fanfics"]) # Create two tabs for movie and fanfic recommendations

# Movie recommender system in the "Movies" tab
tab1.header('Movie Recommender System')
# Dropdown to select a movie
selected_movie_name = tab1.selectbox('Movie?', movies)
# Slider to choose the number of recommendations (between 1 and 10)
number_movies = tab1.slider("How many recs?", 1, 10, 4, key="movies-slider")
# Button to trigger movie recommendations
if tab1.button('Recommend', key="movies-button"):
    tab1.write("Number of recommendations: " + str(number_movies)) # Display the number of recommendations
    names, posters = recommend_movie(selected_movie_name, number_movies)
    cols = tab1.columns(number_movies)
    for i, col in enumerate(cols):
        with col:
            tab1.text(names[i])
            tab1.image(posters[i])

# Fanfic recommender system in the "Fanfics" tab
tab2.header('Fanfiction Recommender System')
# Dropdown to select a fanfic
selected_fanfic_name = tab2.selectbox('Fanfic?', fanfics)
# Slider to choose the number of recommendations (between 1 and 10)
number_fanfics = tab2.slider("How many recs?", 1, 10, 4, key="fanfics-slider")
# Button to trigger fanfic recommendations
if tab2.button('Recommend', key="fanfics-button"):
    tab2.write("Number of recommendations: " + str(number_fanfics)) # Display the number of recommendations
    # Get the fanfic recommendations
    names_fanfic_df = recommend_fanfic(selected_fanfic_name, number_fanfics)
    # Display the recommendations in a dataframe, if available
    if not names_fanfic_df.empty:
        tab2.dataframe(names_fanfic_df) # Display the dataframe with recommendations
    else:
        tab2.write("No recommendations available.") # If no recommendations, show message