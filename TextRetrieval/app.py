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
df_read = pd.read_csv("music.csv")
with open("bm25.pkl", "rb") as tf:
    bm25_read = pickle.load(tf)

df_read.sentiment = df_read.sentiment.astype('int')

st.markdown("# <center>My Kind of Music</center>", unsafe_allow_html=True)
# st.title("My Kind of Music")
# st.write("Find a song on your desired mood and keywords")
st.markdown("#### <center> Find a song on your desired mood and keywords </center>", unsafe_allow_html=True)
st.write("")

st.write("")
st.write("")

st.markdown("## <center> Select the desired mood</center>", unsafe_allow_html=True)
st.write()
# create the line with all face buttons
col1, col2, col3, col4, col5 = st.beta_columns(5)
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

st.write("")
st.write("")

st.markdown("## <center> Provide a few keywords </center>", unsafe_allow_html=True)
query = st.text_input('',value = "")
profanity_filter = st.checkbox('Use profanity filter', value=True)

st.write("")
st.write("")

if mood > 0 and query != "":
    try:
        df_mood = df_read[df_read.sentiment == mood]
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
    except Exception as e:
        st.error("Error entering your query")
        st.write(e)

st.markdown("""***""")
st.caption("by Gunther Bacellar and Pericles Rocha")
