## tokenization_test.py
## Author: Peri Rocha
## TESTING TOKENIZATION WITH NLTK

import nltk
import os

songPath = 'database/D/Dream Theater/Octavarium/Octavarium'

# Opening any file... 
#test_song = open(songPath, 'r', encoding='utf-8').read()
test_song = open(songPath, 'r').read()

#print(test_song)

# Implement tokenization. 

# Requires the 'punkt' package
nltk.download('punkt')
nltk.download('stopwords')

stopwords = nltk.corpus.stopwords.words("english")

#for word in test_song:
    #print(word)

#print(test_song)

tokens = nltk.word_tokenize(test_song)

tokenized_Song = open('tokenization_test_octavarium.txt','w')
for token in tokens:
    if token not in stopwords:
        tokenized_Song.write(token + ' ')

tokenized_Song.close()

