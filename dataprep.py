## sentiment-analysis.py
## Authors: Gunther Bacellar and Pericles Rocha
## SCRIPT TO ANALYZE THE LYRICS DB AND CATEGORIZE SONGS

import nltk
import numpy as np
import os
import pandas as pd
import pickle
#import shutil
import spacy
import sys
import time

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from rank_bm25 import BM25Okapi
from textblob import TextBlob   #Required for language detection

# Determine arguments passed to the script. The script accepts only ONE argument: scope
# Accepted values: 'full','verse','line'
# If no parameters are passed, we will use 'verse' as the default.
# If the argument is invalid, we will halt execution. 
acceptedArgs = ['full','verse','line']
scope = 'verse' #Default

songFile  = 'TextRetrieval/music.csv'
indexFile = 'TextRetrieval/bm25.pkl'

if (len(sys.argv)) > 1: # If parameters passed, see if it is accepted
    scope = sys.argv[1].lower()
    if scope not in acceptedArgs:
        raise Exception("Invalid value for scope argument. Accepted: 'full', 'verse' or 'line'. Provided: ", scope)

# Removes metadata written in the bottom of song files. Metadata starts after a line with a series of underscores ("___...")
def removeLyricMetadata(lyrics):
    cleanLyrics = ''
    for line in lyrics.splitlines():
        # Cut of the metadata part of the lyrics
        if line.startswith('____'):
            return cleanLyrics
        cleanLyrics += line + '\n'
    return cleanLyrics

# Uses tokenization and removes stopwords from lyrics maintaining structure
def removeStopWords(lyrics):
    stopwords = nltk.corpus.stopwords.words("english")

    newLyrics = ''
    for line in lyrics.splitlines():
        tokens = nltk.word_tokenize(line)
        for token in tokens:
            if token not in stopwords:
                newLyrics = newLyrics + token + ' '
        newLyrics = newLyrics + '\n'

    return newLyrics

# Detects the language of the written lyrics
def detectLanguage(lyrics):
    songLanguage = TextBlob(lyrics)
    return songLanguage.detect_language()

# Measures the sentiment for each line in the lyrics and computes an average for the whole song
def getAverageCompound(lyrics, scope='full', addTitle=True, title=''):
    compounds = []
    
    if addTitle:
        lyrics = title + '\n' + '\n' + lyrics

    #Get the sentiment from the FULL lyrics at once
    if scope == 'full':
        sentiment = SentimentIntensityAnalyzer()
        compounds.append(sentiment.polarity_scores(lyrics)['compound'])

    #Get the sentiment from the average of the compounds of each verse
    elif scope == 'verse':
        linecounter = 0
        paragraph = ''
        for line in lyrics.splitlines():
            if line.strip() == '':
                if linecounter > 0: 
                    #Compute the sentiment for a full verse in the lyrics
                    sentiment = SentimentIntensityAnalyzer()
                    verseCompound = sentiment.polarity_scores(paragraph)['compound']
                    if verseCompound != 0:
                        compounds.append(verseCompound)
                    linecounter = 0
                    paragraph = ''
            else:
                paragraph = paragraph + line + '\n'
                linecounter += 1

    #Get the sentiment from the average of the compounds of each line
    elif scope == 'line':
        for line in lyrics.splitlines():
            if len(line.strip()) > 0:
                sentiment = SentimentIntensityAnalyzer()
                compounds.append(sentiment.polarity_scores(line)['compound'])

    meanCompound = 0
    if len(compounds) > 0:     
        meanCompound = np.mean(compounds)

    return meanCompound

def createIndexes():
    print('')
    print('Creating indexes for text retrieval...')

    try:
        # read music dataset
        df = pd.read_csv(songFile)
        nlp = spacy.load("en_core_web_sm")
        bm25 = {}
        # generate the dictionary with 5 different inverted indexes
        for i in range(1,6):
            df_tmp = df[df.sentiment== i].copy()
            df_tmp['lyrics'] = df_tmp['title'] + '\n' + df_tmp['lyrics']
            tok_text=[] # for our tokenised corpus
            for doc in nlp.pipe(df_tmp.lyrics.str.lower().values, disable=["tagger", "ner", "lemmatizer"]):
                tok = [t.text for t in doc if t.is_alpha]
                tok_text.append(tok)
            bm25[i] = BM25Okapi(tok_text)

        # save the dictionary with inverted indexes
        with open(indexFile, 'wb') as tf:
            pickle.dump(bm25,tf)

        print('Indexes created successfully.')
    except Exception as e:
        print('Failure on createIndexes()')
        print(e)

def categorizeSongs(scope):
    print('Attempting to download required package files...')

    # Packages required for tokenization, stopwords, and sentiment analysis
    if (not (nltk.download('punkt', quiet=True))) or (not (nltk.download('stopwords', quiet=True))) or (not nltk.download('vader_lexicon', quiet=True)):
        print('Failed to download required packages. Please verify your internet connection and try again.')
        return
    else: 
        print('Successfully downloaded required package files.')

    dbDir = 'database_source'           # Root directory of the source (original) database

    successesCount = 0          # Songs succesfully categorized
    failedSongsCount = 0        # Songs failed to categorized
    failedSongs = []            # List of songs that failed to categorize
    nonEnglishSongsCount = 0    # Songs not in English
    nonEnglishSongs = []        # List of songs not in English
    shortLyricsCount = 0        # Song files that contain short lyrics (< 24 words)
    shortLyrics = []            # List songs with short lyrics
    songsProcessedCount = 0     # Successes + failed + nonEnglish + empty lyrics

    # Datetime variables for logging purposes
    year = str(time.localtime().tm_year)
    month = str(time.localtime().tm_mon)
    day = str(time.localtime().tm_mday)
    hour = str(time.localtime().tm_hour)
    minutes = str(time.localtime().tm_min)
    seconds = str(time.localtime().tm_sec)
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(hour) == 1:
        hour = '0' + hour
    if len(minutes) == 1:
        minutes = '0' + minutes
    if len(seconds) == 1:
        seconds = '0' + seconds

    # Holds the dataframe that stores the sentiment for each song
    songData = pd.DataFrame(columns = ['title', 'artist', 'lyrics', 'sentiment'])
    
    # Holds the count of songs categorized in each category
    songsByCategory = {
    '1_very_bad': 0,
    '2_bad': 0,
    '3_neutral': 0,
    '4_good': 0,
    '5_very_good': 0
    }

    print('')
    print('Starting Song Sentiment Analysis on directory', os.path.join(os.path.curdir, dbDir), ' at ' + hour + ':' + minutes + ':' + seconds  + ' on ' + month  + '/' + day + '/' + year, 'with scope',scope.upper())
    # Count all files for logging purposes
    print('Counting songs in source directories...')
    fileCount = sum(len(files) for _, _, files in os.walk(dbDir))
    print('Songs detected:', str(fileCount))
    print('')

    # Let's see the sentiment for all lyrics on our DB: 
    startTime = time.time()
    for letter in sorted(os.listdir(dbDir)):
        # For each letter...
        letterPath = os.path.join(dbDir, letter)
        if os.path.isdir(letterPath):
            letters = sorted(os.listdir(letterPath), key=str.lower)
            # ... iterate through artists... 
            for artist in letters:
                artistPath = os.path.join(letterPath, artist)
                if os.path.isdir(artistPath):
                    albums = sorted(os.listdir(artistPath), key=str.lower)
                    # .. then through albuns... 
                    for album in albums:
                        albumPath = os.path.join(artistPath, album)
                        if os.path.isdir(albumPath):
                            songs = sorted(os.listdir(albumPath), key=str.lower)
                            # ... and then each song inside an album.
                            for song in songs:
                                songPath = os.path.join(albumPath, song)
                                if os.path.isfile(songPath): # Is this a file or a directory?
                                    try:
                                        # Read the lyrics file
                                        rawLyrics = open(songPath, 'r', encoding='utf-8').read().strip()
                                        
                                        # Remove metadata before I categorize the song
                                        lyrics = removeLyricMetadata(rawLyrics)

                                        # For some reason, some lyrics are empty. 
                                        # Songs on our database need to have at least 24 words after removing the metadata
                                        if len(lyrics.split()) < 24:
                                            shortLyricsCount += 1
                                            shortLyrics.append(songPath)
                                        else:
                                            # Perform analysis ONLY if lyrics are in English
                                            songLanguage = detectLanguage(lyrics)
                                            if songLanguage != 'en':
                                                nonEnglishSongsCount += 1
                                                nonEnglishSongs.append('(' + songLanguage + '): ' + songPath)
                                            else:
                                                # Run sentiment analyzis and get the compound score. Categorize the song lyrics with a sentiment 1 to 5: 
                                                # 1 Very bad    : compound  < -0.6
                                                # 2 Bad         : compound >= -0.6 and < -0.2
                                                # 3 Neutral     : compound >= -0.2 and <= 0.2
                                                # 4 Good        : compound  >  0.2 and <= 0.6
                                                # 5 Very Good   : compound  >  0.6

                                                # Remove stop words - EVALUATE IF THIS YELDS BETTER RESULTS OR NOT
                                                lyricsNoStopWords = removeStopWords(lyrics)

                                                # Get the compound sentiment. Can be full lyrics, verse or line averages
                                                compound = getAverageCompound(lyricsNoStopWords,scope, True, song)

                                                # NOTE: Sentiment analysis is run on lyrics that are tokenized and WITHOUT stop words. However... 

                                                # ... when we DO categorize songs and want to make them available for search, 
                                                # they will be stored in their original form.

                                                newSong = []
                                                newSong.append(song)
                                                newSong.append(artist)
                                                newSong.append(lyrics)

                                                sentiment = 0
                                                if (compound < -0.6):
                                                    sentiment = 1
                                                    songsByCategory['1_very_bad'] += 1
                                                elif (compound >= -0.6) and (compound < -0.2):
                                                    sentiment = 2
                                                    songsByCategory['2_bad'] += 1
                                                elif (compound >= -0.2) and (compound <= 0.2):
                                                    sentiment = 3
                                                    songsByCategory['3_neutral'] += 1
                                                elif (compound > 0.2) and (compound <= 0.6):
                                                    sentiment = 4
                                                    songsByCategory['4_good'] += 1
                                                elif (compound > 0.6):
                                                    sentiment = 5
                                                    songsByCategory['5_very_good'] += 1

                                                newSong.append(sentiment)
                                                songData.loc[len(songData)] = newSong
                                                successesCount += 1

                                    except Exception as e:
                                        print('Exception: ', e)
                                        print('Current song: ', songPath)
                                        failedSongs.append(songPath)
                                        failedSongsCount += 1

                                    # Print status at every 10%
                                    tenPercent = int(round(fileCount / 10,0))
                                    songsProcessedCount = successesCount + failedSongsCount + nonEnglishSongsCount + shortLyricsCount
                                    if (successesCount > 0) and ((songsProcessedCount) % tenPercent == 0):
                                        percentage = int((songsProcessedCount) / fileCount * 100)
                                        print(str(songsProcessedCount), 'songs analyzed...',''.join(['(', str(percentage),'%)']))

    print(str(successesCount + failedSongsCount + nonEnglishSongsCount + shortLyricsCount), 'songs analyzed. (100%)')
    print('')

    # Finished processing. Save dataframe to CSV
    try:
        songData.to_csv(songFile)
    except Exception as e:
        print('Processing succedded, but failed to write songData file')
        print('Exception: ', e)

    print('Sentiment Analysis categorization complete. Songs were categorized on', songFile)
    print('')
    print('Results:')
    print(' --- Songs analyzed (total):', str(successesCount + failedSongsCount + nonEnglishSongsCount + shortLyricsCount))
    print(' --- Successes.............:', str(successesCount))
    print(' --- Non-English*..........:', str(nonEnglishSongsCount))
    print(' --- Short lyrics*.........:', str(shortLyricsCount))
    print(' --- Failures*.............:', str(failedSongsCount))
    print(' --- Songs in each category:')
    print('           1-Very Bad.........:', str(songsByCategory['1_very_bad']))
    print('           2-Bad..............:', str(songsByCategory['2_bad']))
    print('           3-Neutral..........:', str(songsByCategory['3_neutral']))
    print('           4-Good.............:', str(songsByCategory['4_good']))
    print('           5-Very Good........:', str(songsByCategory['5_very_good']))
    print('   * Check the log file for list of songs')
    print('')

    # Write log file
    logFileName = 'logs/sentiment-analysis-' + year + month+ day+ '_' + hour + minutes

    try: 
        endTime = time.time()
        elapsedTime = endTime - startTime
        logFile = open(logFileName,'w', encoding='utf-8')
        logFile.write('Started running.....: ' + time.asctime(time.localtime(startTime)) +'\n')
        logFile.write('Finished running....: ' + time.asctime(time.localtime(endTime))+'\n')
        logFile.write('Elapsed time........: ' + str(round(elapsedTime,2)) + ' seconds (about ' + str(round(round(elapsedTime,2) / 60,1)) + ' minutes).\n')
        logFile.write('Total songs scanned.: ' + str(fileCount)+'\n')
        logFile.write('Scope...............: ' + scope +'\n')
        logFile.write('Songs categorized...: ' + str(successesCount)+'\n')
        logFile.write('Short lyric files...: ' + str(shortLyricsCount) +'\n')
        logFile.write('Non-english songs...: ' + str(nonEnglishSongsCount)+'\n')    
        logFile.write('Songs failed........: ' + str(failedSongsCount) +'\n')
        logFile.write('Songs per category..: ' + '\n' )
        logFile.write(' --- 1-Very bad.........: ' + str(songsByCategory['1_very_bad']) +'\n')
        logFile.write(' --- 2-Bad..............: ' + str(songsByCategory['2_bad']) +'\n')
        logFile.write(' --- 3-Neutral..........: ' + str(songsByCategory['3_neutral']) +'\n')
        logFile.write(' --- 4-Good.............: ' + str(songsByCategory['4_good']) +'\n')
        logFile.write(' --- 5-Very good........: ' + str(songsByCategory['5_very_good']) +'\n')

        if len(failedSongs) == 0:
            logFile.write('failedSongs: No failures occurred processing songs\n')
        else: 
            logFile.write('List of failed songs: \n')
            for failedSong in failedSongs:
                try: 
                    logFile.write(' --- ' + failedSong +'\n')
                except Exception as e: 
                    logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')
        
        if len(nonEnglishSongs) == 0:
            logFile.write('nonEnglishSongs: No non-English songs were found\n')
        else: 
            logFile.write('List of Non-english songs: \n')    
            for nonEnglishSong in nonEnglishSongs:
                try: 
                    logFile.write(' --- ' + nonEnglishSong +'\n')
                except Exception as e: 
                    logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')

        if len(shortLyrics) == 0:
            logFile.write('shortLyrics: No songs with empty lyrics were found \n')
        else: 
            logFile.write('List of short lyrics on song files: \n')
            for emptyLyric in shortLyrics:
                try: 
                    logFile.write(' --- ' + emptyLyric +'\n')
                except Exception as e: 
                    logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')

        print('Log file written successfully:', logFileName)

    except Exception as e:
        print('Failed to write log file. Exception:', str(e))

    finally:
        logFile.close()

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
#                        SCRIPT STARTS HERE
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
print('===============================================================================================================')
print('||                               MY KIND OF MUSIC - DATA PREPARATION SCRIPT                                  ||')
print('|| Song Sentiment Analysis | V1 | written by Peri Rocha for CS410 Text Information Systems at UIUC           ||')
print('|| Text Retrieval indexing | V1 | written by Gunther  Bacellar for CS410 Text Information Systems at UIUC    ||')
print('|| Use of parts of this program is free as long as we are cited as the source                                ||')
print('|| github.com/periclesrocha                                                                                  ||')
print('===============================================================================================================')
print('')

categorizeSongs(scope)
createIndexes()
print('')