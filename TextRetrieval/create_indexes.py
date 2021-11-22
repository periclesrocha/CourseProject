import pandas as pd
import spacy
import pickle
from rank_bm25 import BM25Okapi
# read music dataset
df = pd.read_csv('music.csv')
nlp = spacy.load("en_core_web_sm")
bm25 = {}
# generate the dictionary with 5 different inverted indexes
for i in range(1,6):
    df_tmp = df[df.sentiment== i].copy()
    df_tmp['lyrics'] = df_tmp['title'] + '\n' + df_tmp['lyrics']
    tok_text=[] # for our tokenised corpus
    for doc in nlp.pipe(df_tmp.lyrics.str.lower().values, disable=["tagger", "ner", "lemmatizer"]):
        tok = [t.text for t in doc if t.is_alpha]
        tok_text.append(tok)
    bm25[i] = BM25Okapi(tok_text)

# save the dictionary with inverted indexes
with open("bm25.pkl", "wb") as tf:
    pickle.dump(bm25,tf)
