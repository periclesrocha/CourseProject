## word_counter.py
## Author: Peri Rocha
## COUNTS WORDS AND SENTENCES IN ALL LYRICS

import os

# TEMP
count_lines = 0
count_words = 0

dbDir = 'database_source'           # Root directory of the source (original) database

# Let's see the sentiment for all lyrics on our DB: 
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
                                lyrics = open(songPath, 'r', encoding='utf-8').read().strip()
                                for line in lyrics.splitlines():
                                    # Cut of the metadata part of the lyrics
                                    if line.startswith('____'):
                                        break
                                    if line != '': # not counting empty lines
                                        count_lines += 1
                                    count_words += len(line.split())

print('Words counted in lyrics: ', count_words)
print('Sentences (lines) counted:', count_lines)
print('Average (words per line):', count_words / count_lines)
