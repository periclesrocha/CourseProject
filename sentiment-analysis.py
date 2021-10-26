## sentiment-analysis.py
## Author: Peri Rocha
## SCRIPT TO ANALYZE THE LYRICS DB AND CATEGORIZE SONGS

import math
import nltk
import os
import time

from nltk.sentiment.vader import SentimentIntensityAnalyzer

dbDir = 'database'
outputDir = 'songs'
nltk.download('vader_lexicon')

def categorizeSong(albumPath, song, sentiment):
    inputPath = os.path.join(albumPath, song)
    outputPath = os.path.join(outputDir, str(sentiment),song)

    lyrics = ''

    try:
        with open(inputPath, 'r', encoding='utf-8',errors='ignore') as lines:
            for line in lines:
                # Cut of the metadata part of the lyrics
                if line.startswith('____'):
                    break
                lyrics += ' ' + line
    except Exception as e:
        print('Could not open source file on song categorization. Error: ', e)

    try:
        outputFile = open(outputPath, 'w', encoding='utf-8',errors='ignore')
        outputFile.write(lyrics)
    except Exception as e:
        print('Could not write destination file on song categorization. Error: ', e)
        print('Failed song: ', inputPath)

    finally: 
        outputFile.close()

def cleanupOutputDir(outputDir):
    count = 0
    for path, dirs, files in os.walk(outputDir):
        for file in files:
            os.remove(os.path.join(path, file))
            count += 1
    return count

successes = 0
failures = 0
failedSongs = []

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
                                    lyrics = open(songPath, 'r', encoding='utf-8',errors='ignore').read().strip()

                                    # THINGS I STILL NEED TO DO: 
                                    # 1) DONE - Clean up the destination folders BEFORE I run the algorithm
                                    # 2) Verify song language and use it only if it's English
                                    # 3) Clean metadata BEFORE getting the sentiment
                                    # 4) Determine if I need to implement tokenization (UNCLEAR OF THIS PACKAGE DOES IT OR NOT)
                                    # 5) Determine if I need to remove stop words

                                    # Run sentiment analyzis and get the compound score. Categorize the lyric with a sentiment: 1 to 5: 
                                    # 1: < -0.6
                                    # 2: >= -0.6 and < -0.2
                                    # 3: >= -0.2 and <= 0.2
                                    # 4: > 0.2 and <= 0.6
                                    # 5: > 0.6
                                    sentiment = SentimentIntensityAnalyzer()
                                    compound = sentiment.polarity_scores(lyrics)['compound']

                                    if (compound < -0.6):
                                        categorizeSong(albumPath, song, 1)
                                    elif (compound >= -0.6) and (compound < -0.2):
                                        categorizeSong(albumPath, song, 2)
                                    elif (compound >= -0.2) and (compound <= 0.2):
                                        categorizeSong(albumPath, song, 3)
                                    elif (compound > 0.2) and (compound <= 0.6):
                                        categorizeSong(albumPath, song, 4)
                                    elif (compound > 0.6):
                                        categorizeSong(albumPath, song, 5)

                                    successes += 1
                                except Exception as e:
                                    print('Exception: ', e)
                                    print('Current song: ', songPath)
                                    failedSongs.append(songPath)
                                    failures += 1

                                # Print status at every 100 songs
                                if math.remainder(successes + failures, 100) == 0:
                                    percentage = round((successes + failures) / fileCount * 100, 2)
                                    print(str(successes + failures), 'songs analyzed...', '(', str(percentage),'% )')


print('Finished organizing songs. Successes: ',str(successes),'Failures: ',str(failures))

# Write log:
try: 
    endTime = time.time()
    elapsedTime = endTime - startTime
    logFile = open('sentiment-analysis.log','w')
    logFile.write('Started running...: ' + time.asctime(time.localtime(startTime)) +'\n')
    logFile.write('Finished running..: ' + time.asctime(time.localtime(endTime))+'\n')
    logFile.write('Elapsed time......: ' + str(round(elapsedTime,2)) + ' seconds.' + '\n')
    logFile.write('Songs categorized.: ' + str(successes)+'\n')
    logFile.write('Songs failed......: ' + str(failures)+'\n')

    for failedSong in failedSongs:
        logFile.writelines(failedSong)

    print('Log file written successfully: sentiment-analysis.log')

except Exception as e:
    print('Failed to write log file. Exception: ', e)

finally:
    logFile.close()
