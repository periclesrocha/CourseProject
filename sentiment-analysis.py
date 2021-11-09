## sentiment-analysis.py
## Author: Peri Rocha
## SCRIPT TO ANALYZE THE LYRICS DB AND CATEGORIZE SONGS

import math
import nltk
import os
import time
import shutil

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob #Required for language detection

nltk.download('punkt') # Required for tokenization
nltk.download('stopwords') # Required for stopwords

dbDir = 'database'
outputDir = 'songs'
nltk.download('vader_lexicon')

def categorizeSong(albumPath, song, sentiment):
    inputPath = os.path.join(albumPath, song)
    outputPath = os.path.join(outputDir, sentiment, song)

    try:
        shutil.copyfile(inputPath, outputPath)
    except Exception as e:
        print('Could copy file on song categorization. Error: ', e)
        print('Failed song: ', inputPath)

def removeLyricMetadata(lyrics):
    cleanLyrics = ''
    for line in lyrics.splitlines():
        # Cut of the metadata part of the lyrics
        if line.startswith('____'):
            return cleanLyrics
        #lyrics += ' ' + line
        cleanLyrics += line + '\n'
    return cleanLyrics

def cleanupOutputDir(outputDir):
    # Delete all files and folders
    count = 0
    for path, dirs, files in os.walk(outputDir):
        for file in files:
            os.remove(os.path.join(path, file))
            count += 1
    
    # Initialize clean folders
    if not os.path.exists(os.path.join(outputDir, '1_negative')):
        os.makedirs(os.path.join(outputDir, '1_negative'))
    if not os.path.exists(os.path.join(outputDir, '2_negative_neutral')):
        os.makedirs(os.path.join(outputDir, '2_negative_neutral'))
    if not os.path.exists(os.path.join(outputDir, '3_neutral')):
        os.makedirs(os.path.join(outputDir, '3_neutral'))
    if not os.path.exists(os.path.join(outputDir, '4_positive_neutral')):
        os.makedirs(os.path.join(outputDir, '4_positive_neutral'))
    if not os.path.exists(os.path.join(outputDir, '5_positive')):
        os.makedirs(os.path.join(outputDir, '5_positive'))

    return count

def removeStopWords(lyrics):
    stopwords = nltk.corpus.stopwords.words("english")
    tokens = nltk.word_tokenize(lyrics)

    newLyrics = ''
    for token in tokens:
        if token not in stopwords:
            newLyrics = newLyrics + token + ' '
    
    return newLyrics

def detectLanguage(lyrics):
    songLanguage = TextBlob(lyrics)
    return songLanguage.detect_language()

successes = 0

failedSongsCount = 0
failedSongs = []
nonEnglishSongsCount = 0
nonEnglishSongs = []

songsByCategory = {
  '1_negative': 0,
  '2_negative_neutral': 0,
  '3_neutral': 0,
  '4_positive_neutral': 0,
  '5_positive': 0
}

startTime = time.time()

print('')
# Count all files for logging purposes
print('Counting songs in subsdirectories... please wait. ')

fileCount = sum(len(files) for _, _, files in os.walk(dbDir))

print('Songs detected: ', str(fileCount))

print('Cleaning up current destination folder...: ')
filesDeleted = cleanupOutputDir(outputDir)
print('Deleted', str(filesDeleted),'files that were previously organized.')

print('Starting song categorization at', time.asctime(time.localtime(startTime)))

# Let's see the sentiment for all lyrics on our DB: 
# For each letter...
for letter in sorted(os.listdir(dbDir)):
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
                        # ... and then songs for each album.
                        for song in songs:
                            songPath = os.path.join(albumPath, song)
                            if os.path.isfile(songPath):
                                try:
                                    #lyrics = open(songPath, 'r', encoding='utf-8',errors='ignore').read().strip()
                                    rawLyrics = open(songPath, 'r', encoding='utf-8').read().strip()
                                    
                                    # Remove metadata before I categorize the song
                                    lyrics = removeLyricMetadata(rawLyrics)

                                    # For some reason, some lyrics are empty. So we'll test that. 
                                    if lyrics != '':
                                        # Perform analysis ONLY if lyrics are English
                                        songLanguage = detectLanguage(lyrics)
                                        if songLanguage != 'en':
                                            nonEnglishSongsCount += 1
                                            nonEnglishSongs.append('(' + songLanguage + '): ' + songPath)
                                        else:
                                            # Run sentiment analyzis and get the compound score. Categorize the lyric with a sentiment: 1 to 5: 
                                            # 1 NEGATIVE: < -0.6
                                            # 2 NEGATIVE-NEUTRAL: >= -0.6 and < -0.2
                                            # 3 NEUTRAL: >= -0.2 and <= 0.2
                                            # 4 POSITIVE-NEUTRAL: > 0.2 and <= 0.6
                                            # 5 POSITIVE: > 0.6

                                            # Remove stop words - EVALUATE IF THIS YELDS BETTER RESULTS OR NOT
                                            lyricsNoStopWords = removeStopWords(lyrics)

                                            sentiment = SentimentIntensityAnalyzer()
                                            
                                            # NOTE: Sentiment analysis is run on lyrics that are tokenized and WITHOUT stop words. However... 
                                            compound = sentiment.polarity_scores(lyricsNoStopWords)['compound']

                                            # ... when we DO categorize songs and want to make them available for search, 
                                            # they will be stored in their original form.
                                            if (compound < -0.6):
                                                categorizeSong(albumPath, song, '1_negative')
                                                songsByCategory['1_negative'] += 1
                                            elif (compound >= -0.6) and (compound < -0.2):
                                                categorizeSong(albumPath, song, '2_negative_neutral')
                                                songsByCategory['2_negative_neutral'] += 1
                                            elif (compound >= -0.2) and (compound <= 0.2):
                                                categorizeSong(albumPath, song, '3_neutral')
                                                songsByCategory['3_neutral'] += 1
                                            elif (compound > 0.2) and (compound <= 0.6):
                                                categorizeSong(albumPath, song, '4_positive_neutral')
                                                songsByCategory['4_positive_neutral'] += 1
                                            elif (compound > 0.6):
                                                categorizeSong(albumPath, song, '5_positive')
                                                songsByCategory['5_positive'] += 1

                                            successes += 1

                                except Exception as e:
                                    print('Exception: ', e)
                                    print('Current song: ', songPath)
                                    failedSongs.append(songPath)
                                    failedSongsCount += 1

                                # Print status at every 100 songs
                                if (successes > 0) and ((successes + failedSongsCount) % 100 == 0):
                                    percentage = round((successes + failedSongsCount) / fileCount * 100, 2)
                                    print(str(successes + failedSongsCount), 'songs analyzed...', '(', str(percentage),'% )')

print(str(successes + failedSongsCount), 'songs analyzed. (100%)')

print('Finished organizing songs. Successes: ',str(successes),'; Failures: ',str(failedSongsCount), '; Non-English: ',str(nonEnglishSongsCount), '; Total: ', str(successes + failedSongsCount + nonEnglishSongsCount))

# Write log:
try: 
    endTime = time.time()
    elapsedTime = endTime - startTime
    logFile = open('sentiment-analysis.log','w', encoding="utf-8")
    logFile.write('Started running...: ' + time.asctime(time.localtime(startTime)) +'\n')
    logFile.write('Finished running..: ' + time.asctime(time.localtime(endTime))+'\n')
    logFile.write('Elapsed time......: ' + str(round(elapsedTime,2)) + ' seconds (about ' + str(round(round(elapsedTime,2) / 60,1)) + ' minutes).\n')
    logFile.write('Songs categorized.: ' + str(successes)+'\n')
    logFile.write('Songs per category: ' + '\n' )
    logFile.write(' --- 1-Negative........: ' + str(songsByCategory['1_negative']) +'\n')
    logFile.write(' --- 2-Negative/Neutral: ' + str(songsByCategory['2_negative_neutral']) +'\n')
    logFile.write(' --- 3-Neutral.........: ' + str(songsByCategory['3_neutral']) +'\n')
    logFile.write(' --- 4-Positive/Neutral: ' + str(songsByCategory['4_positive_neutral']) +'\n')
    logFile.write(' --- 5-Positive........: ' + str(songsByCategory['5_positive']) +'\n')
    logFile.write('Songs failed......: ' + str(failedSongsCount)+'\n')
    for failedSong in failedSongs:
        try: 
            logFile.write(' --- ' + failedSong +'\n')
        except Exception as e: 
            logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')
    
    logFile.write('Non-english songs.: ' + str(nonEnglishSongsCount)+'\n')    
    for nonEnglishSong in nonEnglishSongs:
        try: 
            logFile.write(' --- ' + nonEnglishSong +'\n')
        except Exception as e: 
            logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')

    print('Log file written successfully: sentiment-analysis.log')
except Exception as e:
    print('Failed to write log file. Exception: ', str(e))

finally:
    logFile.close()