import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from glob import glob # when used through directories it will make a list of path names of desired filenames
import json # to parse json files

ROOT_PATH = '../'
        
######## builds dataframe from the full text articles ######

full_text_articles = glob(ROOT_PATH + '*/*/*.json')
# print(full_text_articles[:10])

articles_df = {"sha":[], "article_title":[], "article_authors": [], "location":[], "article_abstract":[], "ref_titles":[], "all_text":[]}

dic = json.load(open(full_text_articles[0]))
print(dic)

count = 0

for path in full_text_articles:
    with open(path) as file:
        article = json.load(file)
        all_text = ""
        articles_df["sha"].append(article["paper_id"])
        try:
            articles_df["article_title"].append(article['metadata']["title"])
            all_text += article['metadata']["title"]
        except:
            articles_df["article_title"].append("")  
        authors_dict = article["metadata"]["authors"]
        authors = ''
        location = ''

        for author in authors_dict:
            try:
                name = author["last"] + ", " + author["first"]
            except:
                name = ""
            authors += name + "; "

            try:
                loc = author['affiliation']['location']['country'] + ':' + author['affiliation']['location']['settlement'] + ';'
                all_text += " " + author['affiliation']['location']['settlement'] + ' ' + author['affiliation']['location']['country']
            except:
                loc=''

            if  loc not in location and loc != '':
                    location += loc
        articles_df["article_authors"].append(authors)
        articles_df['location'].append(location)

        try:
            articles_df["article_abstract"].append(article["abstract"]["text"])
            all_text += ' ' + article["abstract"]["text"]
        except:
            articles_df["article_abstract"].append('')
            
        
        text = ''
        try:
            for paragraph in article['body_text']:
                text += " " + paragraph['text'] 
        finally:
            all_text +=  ' ' + text
        
        ref_titles = []
        try:
            for ref in article['bib_entries']:
                ref_titles.append(article['bib_entries'][ref]['title'])
                all_text += ' ' + article['bib_entries'][ref]['title']
        finally:
            articles_df['ref_titles'].append(ref_titles)
        articles_df["all_text"].append(all_text)
    count += 1
    print("atricle {} has be processed".format(count))

articles_df = pd.DataFrame(data=articles_df)

articles_df.to_pickle("articles_df.pkl")
print('done')

metadata = pd.read_csv(ROOT_PATH + 'metadata.csv', usecols=['sha', 'title', 'doi', 'abstract', 'authors', 'journal'])

df = pd.read_pickle("articles_df.pkl")

new = pd.merge(metadata, df, on="sha", how="outer")

new.to_pickle("merged_data.pkl")
