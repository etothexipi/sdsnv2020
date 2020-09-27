import newspaper
import pandas as pd
import pickle

theonion = newspaper.build('https://theonion.com/')



df = pd.DataFrame({})

for article in theonion.articles[:30]:
    url = article.url
    print(url)
    article = newspaper.Article(url)
    article.download()
    article.parse()

    date = article.publish_date
    blob = article.text

    if article.authors[0]:
        author1 = article.authors[0]
        if article.authors[1]:
            author2 = article.authors[1]
        else:
            author2 = np.nan()
    else:
        author1 = np.nan()
        author2 = np.nan()

    article.nlp()

    if article.keywords[0]:
        keyword1 = article.keywords[0]
        if article.keywords[1]:
            keyword2 = article.keywords[1]
            if article.keywords[2]:
                keyword3 = article.keywords[2]
            else:
                keyword3 = np.nan()
        else:
            keyword2 = np.nan()
            keyword3 = np.nan()
    else:
        keyword1 = np.nan()
        keyword2 = np.nan()
        keyword3 = np.nan()

    df = df.append({'date'    : date,
                    'author1' : author1,
                    'author2' : author2,
                    'blob'    : blob,
                    'keyword1': keyword1,
                    'keyword2': keyword2,
                    'keyword3': keyword3})
    
print(df)    
