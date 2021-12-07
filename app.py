from better_profanity import profanity
import pandas as pd
import pickle
#from rank_bm25 import BM25Okapi
import streamlit as st

musicServiceURL = 'https://music.youtube.com/search?q='

# Always keeps the selected button highlited. 
# Code adapted from https://stackoverflow.com/questions/69478972/how-to-style-a-button-in-streamlit
def style_button_row(clicked_button_ix, n_buttons):
    def get_button_indices(button_ix):
        return {
            'nth_child': button_ix,
            'nth_last_child': n_buttons - button_ix + 1
        }

    clicked_style = """
    div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
        border-color: rgb(255, 75, 75);
        color: rgb(255, 75, 75);
        box-shadow: rgba(255, 75, 75, 0.5) 0px 0px 0px 0.2rem;
        outline: currentcolor none medium;
    }
    """
    unclicked_style = """
    div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
        opacity: 0.65;
        filter: alpha(opacity=65);
        -webkit-box-shadow: none;
        box-shadow: none;
        outline: none;
    }
    """
    style = ""
    for ix in range(n_buttons):
        ix += 1
        if ix == clicked_button_ix:
            style += clicked_style % get_button_indices(ix)
        else:
            style += unclicked_style % get_button_indices(ix)
    st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

def produceSongResult(songIndex, artist, songName, explicit):
    songResult = ''
    songLink = musicServiceURL + songName + ' by '+ artist

    oldSongName = songName
    if explicit:
        songName = profanity.censor(songName)

    # Determines if the song name was changed to obfuscate explicit content
    if (oldSongName != songName):
        songResult = st.markdown(f'{songIndex+1}: <a href="{songLink}" target="_blank" rel="noopener noreferrer"><b><i>{songName}</i></b></a>, by {artist}' + '<b> (Explicit)</b>', unsafe_allow_html=True)
    else: 
        songResult = st.markdown(f'{songIndex+1}: <a href="{songLink}" target="_blank" rel="noopener noreferrer"><b><i>{songName}</i></b></a>, by {artist}', unsafe_allow_html=True)

    return songResult

def renderWebApp():
    st.set_page_config(page_title='My Kind of Music - Find a song on your desired mood and keywords', page_icon='📻', layout='centered', initial_sidebar_state='collapsed', menu_items=None)
    # CSS format to eliminate the right menu page and to format the size of face icons
    st.markdown("""<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;}""", unsafe_allow_html=True)
    st.markdown("""<style> div.stButton > button:first-child {margin-right:-2px; font-size: 40px} </style>""", unsafe_allow_html=True)
    st.markdown(f"""<style>.reportview-container .main .block-container{{padding-top: 5px;}}</style>""",unsafe_allow_html=True,)

    mood = 0  # define first stage with no button (face) selected

    # Initializing 'mood' as a session variable
    # Mood persists through the session despite of callbacks
    if 'mood' not in st.session_state:
        st.session_state['mood'] = 0

    # Read music dataset (csv) and the inverted index dictionary (bm5.pkl)

    df_read = pd.read_csv("TextRetrieval/music.csv")
    with open("TextRetrieval/bm25.pkl", "rb") as tf:
        bm25_read = pickle.load(tf)

    df_read.sentiment = df_read.sentiment.astype('int')

    st.markdown("## Step 1: Select the desired mood", unsafe_allow_html=True)
    st.write()

    # create the line with all face buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if col1.button("😥", on_click=style_button_row,kwargs={'clicked_button_ix': 1, 'n_buttons': 5}):
            st.session_state['mood'] = 1
    with col2:
        if col2.button("☹️", on_click=style_button_row,kwargs={'clicked_button_ix': 2, 'n_buttons': 5}):
            st.session_state['mood'] = 2
    with col3:
        if col3.button("😐", on_click=style_button_row,kwargs={'clicked_button_ix': 3, 'n_buttons': 5}):
            st.session_state['mood'] = 3
    with col4:
        if col4.button("🙂", on_click=style_button_row,kwargs={'clicked_button_ix': 4, 'n_buttons': 5}):
            st.session_state['mood'] = 4
    with col5:
        if col5.button("😀", on_click=style_button_row,kwargs={'clicked_button_ix': 5, 'n_buttons': 5}):
            st.session_state['mood'] = 5

    mood_list = ['very sad', 'sad', 'neutral', 'happy', 'very happy']

    st.write("")
    st.write("")

    st.markdown("## Step 2: Provide a few keywords ", unsafe_allow_html=True)
    query = st.text_input('',value = "")
    profanity_filter = st.checkbox('Use profanity filter', value=True)

    mood = st.session_state['mood']
    if mood > 0 and query != "":
        try:
            # Apply the style to the selected button
            style_button_row(st.session_state['mood'], 5)

            df_mood = df_read[df_read.sentiment == mood]

            tokenized_query = query.lower().split(" ")
            tokenized_query = [x for x in tokenized_query if x!=""]
            st.markdown(f"### <center>Some songs that suggest a *** {mood_list[mood-1]} *** mood</center>", unsafe_allow_html=True)
            #st.write(f"Some songs that suggest the mood {mood_list[mood-1]}")
            # Find the results with best retrieval score in the bm25 dictionary
            results = bm25_read[mood].get_top_n(tokenized_query, df_mood.title.values, n=10)
            col6, col7 = st.columns(2)

            with col6:
                for i in range(5):
                    artist = df_read[df_read.title == results[i]].artist.values[0]
                    # Implementing the profanity filter over the song name
                    # This will be needed for the lyrics in case we decide to show it too 
                    songName = results[i]
                    produceSongResult(i, artist, songName, profanity_filter)
            with col7:
                for i in range(5, 10):
                    artist = df_read[df_read.title == results[i]].artist.values[0]
                    # Implementing the profanity filter over the song name
                    # This will be needed for the lyrics in case we decide to show it too 
                    songName = results[i]
                    produceSongResult(i, artist, songName, profanity_filter)

        except Exception as e:
            st.error("Error entering your query")
            st.write(e)
    st.markdown("""***""")
    st.caption('"My Kind of Music", by Gunther Bacellar and Pericles Rocha',)
    st.caption('github.com/periclesrocha/CourseProject')
    #st.markdown("# <center>My Kind of Music</center>", unsafe_allow_html=True)
    # st.write("Find a song on your desired mood and keywords")
    #st.markdown("##### <center> Find a song on your desired mood and keywords </center>", unsafe_allow_html=True)

renderWebApp()