import pandas as pd
from nltk import SnowballStemmer
import pickle
import gensim

stemmer = SnowballStemmer('english')
problems = []

with open('translated_df.pkl', 'rb') as df:
    translated = pd.read_pickle(df)
    pbar = tqdm(total=len(translated))
    count = 0
    try:
        for text in translated['all_text']:

            try:
                text = gensim.utils.simple_preprocess(text)
                text = ' '.join([stemmer.stem(word) for word in text]).strip(' ') + '\n'
                
                with open('preprocessed_text.cor', 'a+') as f:
                    f.write(text)
                
            except:
                problems.append(count)
                print(translated.loc[count])
            count += 1
            pbar.update(1)
    except:
        pass
    pbar.close()
translated = pd.read_pickle('translated_df.pkl').copy()
translated = translated.drop(problems)
translated.to_pickle('refined.pkl')

model = gensim.models.word2vec.Word2Vec(workers=6, min_count=3)
print('model initalized')
model.build_vocab(corpus_file='preprocessed_text.cor')
print('vocab built')
model.train(corpus_file='preprocessed_text.cor', total_words=model.corpus_count, epochs=model.iter)
print('model trained')
model.save('wv.model')
# model = gensim.models.Word2Vec.load('wv.model')
# print(model.wv.similarity(stemmer.stem('panda'), stemmer.stem('covid')))

