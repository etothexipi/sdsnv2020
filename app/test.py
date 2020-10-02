import newspaper
import pandas as pd

bbc = newspaper.build('https://bbc.com/')

df = pd.DataFrame({})

for article in bbc.articles[:10]:
    url = article.url
    print(url)

