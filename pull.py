import newspaper
import logging
import io
import boto3
import pandas as pd
import pickle
import nltk
import random

nltk.download('punkt')
s3 = boto3.resource('s3')

# Pick random top popular RL and save result
# We need to avoid article/view limits on news sites
top_urls = newspaper.popular_urls()
randtop2 = random.sample(top_urls,2)

for url in randtop2:
    
    cnt = 0

    for article in newspaper.build(url).articles[:3]:

        article.download()
        article.parse()
        article.nlp()

        if url.find('www.') == -1 and url.find('.com') == 1:
            site = url.split('://')[1]
            site = site.split('.com')[0]
        elif url.find('www.') > -1 and url.find('.com') ==1:    
            site = url.split('://www.')[1]
            site = site.split('.com')[0]
            print(site)
        else:
            logging.exception('')
            break

        data = [article.keywords, article.summary]

        pickle_fname = f'newspaper/raw/{site}.{cnt}.pkl'
        pickle_buffer = io.BytesIO()
        #s3_obj = s3.Object(bucket_name='s3://sdsnv2020-etothexipi-intro', key=pickle_fname)

        logging.exception('')

        with open(pickle_buffer, 'wb') as p:
            pickle.dump(data, p)
            s3.Object(bucket_name='s3://sdsnv2020-etothexipi-intro', key=pickle_fname).put(Body=pickle_buffer.getvalue())
            logging.exception('')

        cnt += 1

    logging.exception('')



'''
build = newspaper.build('http://www.technologyreview.com')
articles = build.articles

for article in build.articles[:10]:
    article.download()
    article.parse()
    article.nlp()

    with open(f'./{site}.{y}.pkl', 'wb') as p:
        pickle.dump([article.keywords, article.summary], p)

    y += 1

with open('./build.0.pkl', 'wb') as p:
    pickle.dump(articles, p)

for article in theonion.articles[:30]:
    url = article.url
    print(url)
    article = newspaper.Article(url)
    article.download()
    article.parse()
'''
