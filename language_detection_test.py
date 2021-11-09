## language_detection_test.py
## Author: Peri Rocha
## ATTEMPTING TO DETECT IF THE LANGUAGE IN A SONG IS ENGLISH

import nltk
import os
from textblob import TextBlob

engSongPath = 'database/D/Dream Theater/Octavarium/Octavarium'
deuSongPath = 'database/D/Die Goldenen Zitronen/Kein Mensch ist Illegal/Flimmern'

# Opening any file... 
eng_test_song = open(engSongPath, 'r').read()
deu_test_song = open(deuSongPath, 'r').read()

# For TextBlob to work, you must update translate.py in your environment
# Source: # https://stackoverflow.com/questions/69338699/httperror-http-error-404-not-found-while-using-translation-function-in-textb
# On my PC, this file could be found on C:\Users\procha\Anaconda3\envs\cs410-tis\Lib\site-packages\textblob\translate.py

engDetect = TextBlob(eng_test_song)
deuDetect = TextBlob(deu_test_song)

print('Song A: ', engDetect.detect_language())
print('Song B: ', deuDetect.detect_language())