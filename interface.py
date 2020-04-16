import pandas as pd
import gensim.models as gm
from gensim.utils import simple_preprocess
import numpy as np
import pickle
from nltk import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

stemmer = SnowballStemmer('english')
model = gm.Word2Vec.load('wv.model')

def get_topic_vec(topic):
    topic = simple_preprocess(topic)
    topic = [stemmer.stem(word) for word in topic]
    if len(topic) != 1:
        topic_vec = np.zeros(100)
        for word in topic:
            try:
                topic_vec += model.wv[word]
            except KeyError:
                pass
        topic_vec /= len(topic)
    else:
        try:
            topic_vec = model.wv[topic[0]]
        except KeyError:
            topic = input('That is not a valid keyword choice.\nPlease enter one or more keywords: ')
            topic_vec = get_topic_vec(topic)
    return topic_vec

topic = input('Articles can be searched for based on one or more keywords.\nWords must be separated, do not click "Enter" between keyword entries.\n(All article print outs are in english and have been translated using google translate)\nInput the keyword(s) for your search: ')
topic_vec = get_topic_vec(topic)

read = True
count = 0
with open('doc_vecs.pkl', 'rb') as vecs:
    pbar = tqdm(total=len(pd.read_pickle('refined.pkl')))
    cos_sim = []
    while read == True:
        try:
            vec = pickle.load(vecs)
            sim = cosine_similarity([topic_vec], [vec])[0][0]
            if len(cos_sim) <= 10:
                cos_sim.append((sim, count))
            else:
                if sim > min(cos_sim)[0]:
                    cos_sim.remove(min(cos_sim))
                    cos_sim.append((sim, count))

        except EOFError:
            read = False
        pbar.update(1)
        count += 1
    pbar.close()
 
article_df = pd.read_pickle('refined.pkl')
aritcle_df = article_df.reset_index(drop=True, inplace=True)
# needed to reset here as saving it causes a memory error
articles = article_df.loc[[i[1] for i in cos_sim],['doi', 'title', 'authors', 'abstract']]
articles.insert(loc=0, column='score', value=[i[0] for i in cos_sim])

print(articles.sort_values(by=['score'], ascending=False).to_string(index=False))
