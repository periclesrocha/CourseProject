# Parameter examples
query = "true love"   # Query elements
mood = 1              # 1:very sad, 2:sad, 3:neutral, 4: good, 5: very good
n_results = 5        # Number of results to be shown

mood = int(input("What is your mood from 1-5 (1-very sad, 5-very good)? "))
query = input("What are your query words? ")
n_results = int(input("How many results to show (number)? "))
result = input("Show only title in results (y/n)?")

import os
import sys
import time
import pandas as pd
import spacy
import pickle
from rank_bm25 import BM25Okapi

mypath = ''

# Reading offline dataset (csv) and tokenized file
df_read = pd.read_csv(os.path.join(mypath, "music.csv"))
with open("bm25.pkl", "rb") as tf:
    bm25_read = pickle.load(tf)

# Creating the query and print title results
df_read.type = df_read.type.astype('int')
df_mood = df_read[df_read.type == mood]
tokenized_query = query.lower().split(" ")

t0 = time.time()
results = bm25_read[mood].get_top_n(tokenized_query, df_mood.title.values, n=n_results)
t1 = time.time()
print(f'Searched {len(df_mood)} records in {round(t1-t0,3) } seconds \n')
for i in range(len(results)):
  print(f'Result #{i+1}: {results[i]}')

# Printing title and text of results
if result != 'y':
  for i in range(len(results)):
      df_result = df_mood[df_mood.title == results[i]]
      print("___________________________________")
      print ("")
      print (f"Result #{i+1}: {df_result.title.values[0]}")
      print (df_result.text.values[0])
