import streamlit as st
import os
import pandas as pd
import spacy
import pickle
from better_profanity import profanity
from rank_bm25 import BM25Okapi

mood = 0  # define first stage with no button (face) selected

# CSS format to eliminate the right menu page and to format the size of face icons
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)
st.markdown("""
<style> 
div.stButton > button:first-child {
margin-right:-4px; font-size: 40px
}
</style>
""", unsafe_allow_html=True)

# Read music dataset (csv) and the inverted index dictionary (bm5.pkl)
df_read = pd.read_csv("./files/music.csv")
with open("./files/bm25.pkl", "rb") as tf:
    bm25_read = pickle.load(tf)
df_read.type = df_read.type.astype('int')

st.title("My Kind of Music")
st.write("")
st.write("Find a song on your desired mood and keywords")
st.write("By Gunther Bacellar and Pericles Rocha")
query = st.text_input('Provide a few keywords:',value = "")
profanity_filter = st.checkbox('Profanity filter', value=True)

st.write("Select the desired mood of the music:")
# create the line with all face buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if col1.button("😥"):
        mood = 1
with col2:
    if col2.button("☹️"):
        mood = 2
with col3:
    if col3.button("😐"):
        mood = 3
with col4:
    if col4.button("🙂"):
        mood = 4
with col5:
    if col5.button("😀"):
        mood = 5

mood_list = ['very sad', 'sad', 'neutral', 'happy', 'very happy']

if mood > 0 and query != "":
    try:
        df_mood = df_read[df_read.type == mood]
        # Change query, eliminate profanity if filter is activated
        if profanity_filter:
            query = profanity.censor(query).replace('*', '')
        # clean tokenized words
        tokenized_query = query.lower().split(" ")
        tokenized_query = [x for x in tokenized_query if x!=""]
        st.write(f"Some songs that suggest the mood {mood_list[mood-1]}")
        # Find the results with best retrieval score in the bm25 dictionary
        results = bm25_read[mood].get_top_n(tokenized_query, df_mood.title.values, n=10)
        for i in range(len(results)):
            artist = df_read[df_read.title == results[i]].artist.values[0]
            st.write(f"Song {i+1}: {results[i]}, by artist {artist}")
    except:
        st.write("")
        st.error("Error entering your query")

