import logging
import json
from datetime import datetime
import io
import boto3
import random
import os
from newsapi import NewsApiClient

# Initialize NewsApi Client with Key
NEWSAPI_KEY = os.environ['NEWSAPI_KEY']
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# Try to pull parameters from environment (for container usage)
# Else define defaults here
if all(param in ['STARTPULL', 'ENDPULL', 'QUERYPULL'] for param in os.environ) is True:
    STARTPULL = os.environ['STARTPULL']
    ENDPULL = os.environ['ENDPULL']
    QUERYPULL = os.environ['QUERYPULL']
else:
    STARTPULL = datetime.today().strftime('%Y-%m-%d')
    ENDPULL = STARTPULL
    QUERYPULL = 'cryptocurrency'

# Get top 10 pages of results by  relevancy
for PAGEPULL in range(1,10):
    news_pull = newsapi.get_everything(q=QUERYPULL,
                                       from_param=STARTPULL,
                                       to=ENDPULL,
                                       language='en',
                                       sort_by='relevancy',
                                       page=PAGEPULL)
    if news_pull['articles'] == []:
        break

logging.exception('')
print(f'Stopped on page: {PAGEPULL}')
print(news_pull)

# Put JSON as string to S3
s3 = boto3.resource('s3')
