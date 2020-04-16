import pandas as pd
import gensim.models as gm
import numpy as np
import pickle

model = gm.Word2Vec.load('wv.model')
articles_df = pd.read_pickle('refined.pkl')['sha']

count = 0

with open('preprocessed_text.cor', 'r') as docs:
    while count < len(articles_df):
        doc = docs.readline().strip('\n').split(' ')
        vec = np.zeros(100)
        for word in doc:
            try:
                vec += model.wv[word]
            except:
                pass
        vec /= len(doc)
        with open('doc_vecs.pkl', 'ab') as f:
            pickle.dump(vec, f)
        count += 1
        print('{}/44970'.format(count))

