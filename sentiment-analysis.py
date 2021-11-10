## sentiment-analysis.py
## Author: Peri Rocha
## SCRIPT TO ANALYZE THE LYRICS DB AND CATEGORIZE SONGS

import nltk
import os
import time
import shutil
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob   #Required for language detection

# Copies song lyrics files from source (orinal) directory to categorized (destination) directory for text retrieaval 
def copyToCategorizedDir(albumPath, song, album, artist, outputDir, sentiment):
    inputPath = os.path.join(albumPath, song)

    # Destination file name will be '[songname] ([album], by [artist])
    outputPath = os.path.join(outputDir, sentiment, song) + ' (' + album +', by ' + artist + ')'

    try:
        shutil.copyfile(inputPath, outputPath)
    except Exception as e:
        print('Could not copy file on song categorization. Error: ', e)
        print('Failed song: ', inputPath)

# Removes metadata written in the bottom of song files. Metadata starts after a line with a series of underscores ("___...")
def removeLyricMetadata(lyrics):
    cleanLyrics = ''
    for line in lyrics.splitlines():
        # Cut of the metadata part of the lyrics
        if line.startswith('____'):
            return cleanLyrics
        cleanLyrics += line + '\n'
    return cleanLyrics

# Uses tokenization and removes stopwords from lyrics
def removeStopWords(lyrics):
    stopwords = nltk.corpus.stopwords.words("english")
    tokens = nltk.word_tokenize(lyrics)

    newLyrics = ''
    for token in tokens:
        if token not in stopwords:
            newLyrics = newLyrics + token + ' '
    
    return newLyrics

# Detects the language of the written lyrics
def detectLanguage(lyrics):
    songLanguage = TextBlob(lyrics)
    return songLanguage.detect_language()

# Cleans up categorized (destination) directories ahead of categorization
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

def categorizeSongs():
    nltk.download('punkt')          #Required for tokenization
    nltk.download('stopwords')      #Required for stopwords
    nltk.download('vader_lexicon')  #Required for sentiment analysis

    dbDir = 'database_source'           # Root directory of the source (original) database
    outputDir = 'database_categorized'  # Root directory of the categorized (destination) database

    successesCount = 0          # Songs succesfully categorized
    failedSongsCount = 0        # Songs failed to categorized
    failedSongs = []            # List of songs that failed to categorize
    nonEnglishSongsCount = 0    # Songs not in English
    nonEnglishSongs = []        # List of songs not in English
    emptyLyricsCount = 0        # Song files that contain no lyrics

    #TEMP
    counter = 0

    # Holds the count of songs categorized in each category
    songsByCategory = {
    '1_negative': 0,
    '2_negative_neutral': 0,
    '3_neutral': 0,
    '4_positive_neutral': 0,
    '5_positive': 0
    }

    print('')
    # Count all files for logging purposes
    print('Counting songs in subsdirectories... please wait. ')
    fileCount = sum(len(files) for _, _, files in os.walk(dbDir))
    print('Songs detected: ', str(fileCount))

    # Clean existing files
    print('Cleaning up current destination folder...: ')
    filesDeleted = cleanupOutputDir(outputDir)
    print('Deleted', str(filesDeleted),'files that were previously organized.')

    # Let's see the sentiment for all lyrics on our DB: 
    startTime = time.time()
    print('Starting song categorization at', time.asctime(time.localtime(startTime)))
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

                                        # For some reason, some lyrics are empty. So we'll test that. 
                                        if lyrics == '':
                                            emptyLyricsCount += 1
                                        else:
                                            # Perform analysis ONLY if lyrics are in English
                                            songLanguage = detectLanguage(lyrics)
                                            if songLanguage != 'en':
                                                nonEnglishSongsCount += 1
                                                nonEnglishSongs.append('(' + songLanguage + '): ' + songPath)
                                            else:
                                                # Run sentiment analyzis and get the compound score. Categorize the song lyrics with a sentiment 1 to 5: 
                                                # 1 NEGATIVE        : compound  < -0.6
                                                # 2 NEGATIVE-NEUTRAL: compound >= -0.6 and < -0.2
                                                # 3 NEUTRAL         : compound >= -0.2 and <= 0.2
                                                # 4 POSITIVE-NEUTRAL: compound  >  0.2 and <= 0.6
                                                # 5 POSITIVE        : compound  >  0.6

                                                # Remove stop words - EVALUATE IF THIS YELDS BETTER RESULTS OR NOT
                                                lyricsNoStopWords = removeStopWords(lyrics)

                                                sentiment = SentimentIntensityAnalyzer()
                                                
                                                # NOTE: Sentiment analysis is run on lyrics that are tokenized and WITHOUT stop words. However... 
                                                compound = sentiment.polarity_scores(lyricsNoStopWords)['compound']

                                                # ... when we DO categorize songs and want to make them available for search, 
                                                # they will be stored in their original form.
                                                if (compound < -0.6):
                                                    copyToCategorizedDir(albumPath, song, album, artist, outputDir, '1_negative')
                                                    songsByCategory['1_negative'] += 1
                                                elif (compound >= -0.6) and (compound < -0.2):
                                                    copyToCategorizedDir(albumPath, song, album, artist, outputDir, '2_negative_neutral')
                                                    songsByCategory['2_negative_neutral'] += 1
                                                elif (compound >= -0.2) and (compound <= 0.2):
                                                    copyToCategorizedDir(albumPath, song, album, artist, outputDir, '3_neutral')
                                                    songsByCategory['3_neutral'] += 1
                                                elif (compound > 0.2) and (compound <= 0.6):
                                                    copyToCategorizedDir(albumPath, song, album, artist, outputDir, '4_positive_neutral')
                                                    songsByCategory['4_positive_neutral'] += 1
                                                elif (compound > 0.6):
                                                    copyToCategorizedDir(albumPath, song, album, artist, outputDir, '5_positive')
                                                    songsByCategory['5_positive'] += 1

                                                successesCount += 1

                                    except Exception as e:
                                        print('Exception: ', e)
                                        print('Current song: ', songPath)
                                        failedSongs.append(songPath)
                                        failedSongsCount += 1

                                    # Print status at every 100 songs
                                    # This is a little buggy - I'll correct it later
                                    if (successesCount > 0) and ((successesCount + failedSongsCount + nonEnglishSongsCount + emptyLyricsCount) % 100 == 0):
                                        percentage = round((successesCount + failedSongsCount + nonEnglishSongsCount + emptyLyricsCount) / fileCount * 100, 2)

                                        print(str(successesCount + failedSongsCount), 'songs analyzed...',''.join(['(', str(percentage),'%)']))

    print(str(successesCount + failedSongsCount), 'songs analyzed. (100%)')
    print('Finished organizing songs. Successes: ',str(successesCount),'; Failures: ',str(failedSongsCount), '; Non-English: ',str(nonEnglishSongsCount), '; Empty files: ',str(emptyLyricsCount), '; Total: ', str(successesCount + failedSongsCount + nonEnglishSongsCount))

    # Write log file
    year = str(time.localtime().tm_year)
    month = str(time.localtime().tm_mon)
    day = str(time.localtime().tm_mday)
    hour = str(time.localtime().tm_hour)
    min = str(time.localtime().tm_min)

    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(hour) == 1:
        hour = '0' + hour
    if len(min) == 1:
        min = '0' + min

    logFileName = 'logs/sentiment-analysis-' + year + month+ day+ '_' + hour + min

    try: 
        endTime = time.time()
        elapsedTime = endTime - startTime
        logFile = open(logFileName,'w', encoding="utf-8")
        logFile.write('Started running.....: ' + time.asctime(time.localtime(startTime)) +'\n')
        logFile.write('Finished running....: ' + time.asctime(time.localtime(endTime))+'\n')
        logFile.write('Elapsed time........: ' + str(round(elapsedTime,2)) + ' seconds (about ' + str(round(round(elapsedTime,2) / 60,1)) + ' minutes).\n')
        logFile.write('Total songs scanned.: ' + str(fileCount)+'\n')
        logFile.write('Songs categorized...: ' + str(successesCount)+'\n')
        logFile.write('Empty lyrics files..: ' + str(emptyLyricsCount) +'\n')
        logFile.write('Non-english songs...: ' + str(nonEnglishSongsCount)+'\n')    
        logFile.write('Songs failed........: ' + str(failedSongsCount) +'\n')
        logFile.write('Songs per category..: ' + '\n' )
        logFile.write(' --- 1-Negative........: ' + str(songsByCategory['1_negative']) +'\n')
        logFile.write(' --- 2-Negative/Neutral: ' + str(songsByCategory['2_negative_neutral']) +'\n')
        logFile.write(' --- 3-Neutral.........: ' + str(songsByCategory['3_neutral']) +'\n')
        logFile.write(' --- 4-Positive/Neutral: ' + str(songsByCategory['4_positive_neutral']) +'\n')
        logFile.write(' --- 5-Positive........: ' + str(songsByCategory['5_positive']) +'\n')

        logFile.write('List of failed songs: \n')
        for failedSong in failedSongs:
            try: 
                logFile.write(' --- ' + failedSong +'\n')
            except Exception as e: 
                logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')
        
        logFile.write('List of Non-english songs: \n')    
        for nonEnglishSong in nonEnglishSongs:
            try: 
                logFile.write(' --- ' + nonEnglishSong +'\n')
            except Exception as e: 
                logFile.write(' --- <FAILED TO WRITE SONG NAME IN LOG FILE> (Exception: ' + str(e) + ')' + '\n')

        print('Log file written successfully: ', logFileName)
    except Exception as e:
        print('Failed to write log file. Exception: ', str(e))

    finally:
        logFile.close()


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
#                        SCRIPT STARTS HERE
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

categorizeSongs()
