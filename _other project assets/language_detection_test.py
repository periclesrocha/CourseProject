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
# Replace the url line with
# url = "http://translate.google.com/translate_a/t?client=te&format=html&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=2&ssel=0&tsel=0&kc=1"


engDetect = TextBlob(eng_test_song)
deuDetect = TextBlob(deu_test_song)

print('Song A: ', engDetect.detect_language())
print('Song B: ', deuDetect.detect_language())