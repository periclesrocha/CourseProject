## tests.py
## Author: Peri Rocha
## RANDOM TESTING WITH DIFFERENT PACKAGES

srcDir = 'database'

from transformers import pipeline

sentiment_analysis = pipeline('sentiment-analysis')

sentence = ''

# Negative: [{'label': 'NEGATIVE', 'score': 0.9949591}]
#with open('database/D/Dream Theater/Octavarium/Octavarium') as lines:

# Negative 2: 
#with open('database/S/Slipknot/Vol. 3 - The Subliminal Verses/Duality') as lines:

# Positive: [{'label': 'POSITIVE', 'score': 0.9972928}]
with open('database/R/Rush/Counterparts/The Speed of Love') as lines:
  for line in lines:
    # Cut of the metadata part of the lyrics
    if line.startswith('____'):
          break
    sentence += ' ' + line

# Sanity check
print(sentence)

result = sentiment_analysis(sentence)

print(result)
#print("Label:", result['label'])
#print("Confidence Score:", result['score'])

# Example: 
#pos_text = 'I enjoy studying computational algorithms.'
#neg_text = 'I dislike sleeping late everyday.'

# result = sentiment_analysis(pos_text)[0]
# print("Label:", result['label'])
# print("Confidence Score:", result['score'])
# print()
# result = sentiment_analysis(neg_text)[0]
# print("Label:", result['label'])
# print("Confidence Score:", result['score'])

print('')
print('')
print('=================')
print('NLTK')
print('=================')
print('')
print('')

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
print(sid.polarity_scores(sentence)['compound'])

# Let's see the sentiment for all lyrics on our DB: 

import os

sentiments = []
compounds = []

# 1. Loop through letters in the database
# print('Directories: ', sorted(os.listdir(srcDir)))
for letter in sorted(os.listdir(srcDir)):
    letterPath = os.path.join(srcDir, letter)
    if os.path.isdir(letterPath):
        letters = sorted(os.listdir(letterPath), key=str.lower)
        # 2. Loop through artists starting with letter x
        for artist in letters:
            artistPath = os.path.join(letterPath, artist)
            if os.path.isdir(artistPath):
                albums = sorted(os.listdir(artistPath), key=str.lower)
                # 3. Loop through artist's albums
                for album in albums:
                    albumPath = os.path.join(artistPath, album)
                    if os.path.isdir(albumPath):
                        songs = sorted(os.listdir(albumPath), key=str.lower)
                        # 4. Loop through songs
                        for song in songs:
                            songPath = os.path.join(albumPath, song)
                            if os.path.isfile(songPath):
                                try:
                                    lyrics = open(songPath, 'r').read().strip()
                                    sid = SentimentIntensityAnalyzer()
                                    sentiments.append(sid.polarity_scores(lyrics))

                                    # Categorize the lyric: 1 to 5: 
                                    # 1: < -0.6
                                    # 2: >= -0.6 and < -0.2
                                    # 3: >= -0.2 and <= 0.2
                                    # 4: > 0.2 and <= 0.6
                                    # 5: > 0.6

                                    # Categorize the lyric: 1 to 5: 
                                    # 1: < -0.33
                                    # 3: >= -0.33 and <= 0.33
                                    # 5: > 0.33

                                    compound = sid.polarity_scores(lyrics)['compound']
                                    
                                    # Initializes with 1 and changes only if needed
                                    sentiment_score = 1

                                    ## USING a 5 grades scale 
                                    #if (compound >= -0.6) and (compound < -0.2):
                                    #    sentiment_score = 2
                                    #elif (compound >= -0.2) and (compound <= 0.2):
                                    #    sentiment_score = 3
                                    #elif (compound > 0.2) and (compound <= 0.6):
                                    #    sentiment_score = 4
                                    #elif (compound > 0.6):
                                    #    sentiment_score = 5

                                    ## USING a 3 grades scale 
                                    if (compound >= -0.33) and (compound <= 0.33):
                                        sentiment_score = 2
                                    elif (compound > 0.33):
                                        sentiment_score = 3

                                    compounds.append(str(compound) + ','+ str(sentiment_score))
                                except:
                                    print('Error reading ', songPath)

output_file = open('sentiments.txt','w')

for sentiment in sentiments:
     output_file.write(str(sentiment))
     output_file.write('\n')
output_file.close()

output_file = open('compounds.txt','w')

for compound in compounds:
     output_file.write(str(compound))
     output_file.write('\n')
output_file.close()