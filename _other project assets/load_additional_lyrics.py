## load_additional_lyrics.py
## Author: Pericles Rocha
## ADDITIONAL LOAD SCRIPT FOR 1k SONG DB

import os
import pandas as pd

newLyricsDF = data = pd.read_csv('train_lyrics_1000.csv') 
unwantedWords = ['chorus','(chorus)','(chorus:)',
                 '(chorus 2:)','[chorus x2]','*chorus starts*',
                 'chorus:','[chorus]','(pre-chorus)','(repeat-chorus)',
                 '(bridge and chorus)','[repeat chorus]','(verse 1:)', 
                 '(verse 2:)', '(verse 3:)', '[verse 1:]','[verse 2:]',
                 '[Repeat verses 1 & 2]']

dbDir = os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)),'database_source')

# file,artist,title,lyrics,genre,mood,year
for index, row in newLyricsDF.iterrows():
    artist = row['artist']
    song = row['title']
    lyrics = row['lyrics'] 

    # Clean up lyrics
    cleanLyrics = ''
    for line in lyrics.splitlines():
        # Cut of the metadata part of the lyrics
        words = line.split()
        line = [word for word in words if word not in unwantedWords]
        newLine = ''
        for word in line:
            newLine = newLine + word + ' '
        cleanLyrics = cleanLyrics + newLine.strip() + '\n'

    # Add metadata to the end of the file
    cleanLyrics = cleanLyrics + '\n'
    cleanLyrics = cleanLyrics + '\n'
    cleanLyrics = cleanLyrics + '_______________' + '\n'
    cleanLyrics = cleanLyrics + 'Name    ' + song + '\n'
    cleanLyrics = cleanLyrics + 'Artist  ' + artist + '\n'
    cleanLyrics = cleanLyrics + 'Album   ' + '__unknown_album \n'

    songFolder = os.path.join(dbDir, artist[:1],artist,'__unknown_album')

    if not os.path.exists(songFolder):
        os.makedirs(songFolder)    

    songFile = open(os.path.join(songFolder,song), 'w', encoding='UTF-8')
    songFile.write(cleanLyrics)
    songFile.close()
