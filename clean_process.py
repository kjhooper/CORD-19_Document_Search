import pandas as pd
from googletrans import Translator
import numpy as np
import subprocess
import sys
import glob

vpn_root = './vpns/*.bash'
vpns = []
for script in glob.glob(vpn_root):
    vpns.append(script)

def translate_text(title, abstract, all_text):
    translator = Translator(service_urls=['translate.google.ca'])
    lang = 'en'
    try:
        if title != '':
            lang = translator.detect(title).lang
        else:
            raise TypeError
    except TypeError:
        try:
            if abstract != '':
                try:
                    lang = translator.detect(abstract[:200]).lang
                except:
                    pass
            else:
                raise TypeError
        except:
            try:
                lang = translator.detect(all_text[:200]).lang
            except:
                pass
    print(lang)

    if lang != 'en':

        try:
            title = translator.translate(title).text
        except:
            pass
        try:
            abstract = translator.translate(abstract).text
        except:
            pass
        try:
            title = translator.translate(all_text).text
        except:
            pass
    return(title, abstract, all_text)


data = pd.read_pickle('merged_data.pkl')

temp_df = {'sha':[], 'doi':[], 'title':[], 'authors':[], 'abstract':[], 'journal':[], 'location':[], 'all_text':[]}

count = 0
try:
    while count < len(data):

        if not (pd.isnull(data['title'][count]) and 
            pd.isnull(data['article_title'][count]) and 
            (pd.isnull(data['abstract'][count] or 
            data['abstract'][count] != 'Unknown'))):

            if pd.isnull(data['sha'][count]):

                all_text = ''

                if not pd.isnull(data['title'][count]):
                    title = data['title'][count]
                    try:
                        all_text += data['title'][count]
                    except:
                        print("could not add title to all_text")
                        print(type(data['title'][count]))
                        title = data['article_title'][count]
                else:
                    title = data['article_title'][count]
                    all_text = data['all_text'][count]
                
                if not pd.isnull(data['authors'][count]):
                    authors = data['authors'][count]
                else:
                    authors = data['article_authors'][count]
                
                if not pd.isnull(data['abstract'][count]):
                    abstract = data['abstract'][count]
                    try:
                        all_text += ' ' + data['abstract'][count]
                    except:
                        abstract = data['article_abstract'][count]
                        print("could not add abstract to all_text")
                        print(type(data['abstract'][count]))
                else:
                    abstract = data['article_abstract'][count]
                    
            else:
                all_text = data['all_text'][count]
                
                if data['article_title'][count] == '' and not pd.isnull(data['title'][count]):
                    
                    all_text += ' ' + data['title'][count]
                
                if data['article_abstract'][count] == '' and not pd.isnull(data['abstract'][count]):
                    
                    all_text += ' ' + data['abstract'][count]
                
                if data['article_title'][count] != '':
                    title = data['article_title'][count]
                else:
                    title = data['title'][count]

                if data['article_authors'][count] != '':
                    authors = data['article_authors'][count]
                else:
                    authors = data['authors'][count]

                if data['article_abstract'][count] != '':
                    abstract = data['article_abstract'][count]
                else:
                    abstract = data['abstract'][count]
        
        try:
            title, abstract, all_text = translate_text(title, 
            abstract, all_text)
        
        except:
            i = 0
            while True and i < 5:
                try:
                    script = np.random.choice(vpns, 1)
                    process = subprocess.call(['bash', script[0]])
                    title, abstract, all_text = translate_text(title, abstract, all_text)
                    break
                except:
                    print('Error is:', sys.exc_info()[0])
                    print('refreshing vpn')
                    i += 1
            pass

        temp_df['sha'].append(data['sha'][count])
        temp_df['doi'].append(data['doi'][count])
        temp_df['title'].append(title)
        temp_df['authors'].append(authors)
        temp_df['abstract'].append(abstract)
        temp_df['journal'].append(data['journal'][count])
        temp_df['location'].append(data['location'][count])
        temp_df['all_text'].append(all_text)

        count += 1
        print('{}/{}'.format(count, len(data)))
except:
    print('could not complete error was:', sys.exc_info[0])
    pass

for i in temp_df:
    print(i, len(temp_df[i]))

refined_df = pd.DataFrame(temp_df)
refined_df.to_pickle('translated_df.pkl')
