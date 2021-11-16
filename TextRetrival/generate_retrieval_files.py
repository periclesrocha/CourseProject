import os
import pandas as pd
import spacy
import pickle
from rank_bm25 import BM25Okapi

url_db = ".\database_categorized"
df = pd.DataFrame(columns = ["url", "type", "title", "artist", "text"])
for root, dirs, files in os.walk(url_db):
    for filepath in files:
        classification = root.split('\\')[-1].split('_')[0]
        file_name = os.path.join(root, filepath)
        music = []
        temp_out = ''
        with open(file_name, 'r', encoding='utf-8-sig') as file:
            music.append(file_name)
            music.append(classification)
            end = False
            for line in file:
                if line[:3] == "___":
                    end = True
                if end == False:
                    temp_out += line
                else:
                    line = line.strip().split()
                    if line == []: 
                        break
                    if line[0] in ["Name", "Artist"]:
                        music.append(" ".join(line[1:]))
            music.append(temp_out)
        df.loc[len(df)] = music

# Tokenizing using SpaCy
nlp = spacy.load("en_core_web_sm")
bm25 = {}
for i in range(1,6):
    df_tmp = df[df.type == str(i)]
    tok_text=[] # for our tokenised corpus
    for doc in nlp.pipe(df_tmp.text.str.lower().values, disable=["tagger", "ner", "lemmatizer"]):
        tok = [t.text for t in doc if t.is_alpha]
        tok_text.append(tok)
    bm25[i] = BM25Okapi(tok_text)

# Generating offline dataset and tokenized file 
df.to_csv("music.csv", encoding='utf-8-sig')
with open("bm25.pkl", "wb") as tf:
    pickle.dump(bm25,tf)