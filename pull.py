import logging
import json
from datetime import datetime, timedelta
import io
import boto3
import random
import os
from newsapi import NewsApiClient

# Initialize NewsApi Client with Key
NEWSAPI_KEY = os.environ['NEWSAPI_KEY']
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# Initialize S3 Bucket
S3BUCKETNAME = os.environ['S3BUCKETNAME']
s3 = boto3.client('s3')

# Try to pull parameters from environment (for container usage)
# Else define defaults 
if all(param in ['STARTPULL', 'ENDPULL', 'QUERYPULL'] for param in os.environ) is True:
    STARTPULL = os.environ['STARTPULL']
    ENDPULL = os.environ['ENDPULL']
    QUERYPULL = os.environ['QUERYPULL']
else:
    print(f'WARNING: Job params not all defined in environment. Running defaults')
    yesterday = datetime.today() + timedelta(days=-1)
    STARTPULL = yesterday.strftime('%Y-%m-%d')
    ENDPULL = STARTPULL
    QUERYPULL = 'cryptocurrency'

# Get up to 10 pages of results by relevancy
for PAGEPULL in range(1,10):
    news_pull = newsapi.get_everything(q=QUERYPULL,
                                       from_param=STARTPULL,
                                       to=ENDPULL,
                                       language='en',
                                       sort_by='relevancy',
                                       page=PAGEPULL)

    # Put JSON as string to S3
    json_text = json.dumps(news_pull)
    s3.put_object(Bucket=S3BUCKETNAME,
                  Key=f'{STARTPULL}-{QUERYPULL}-page-{PAGEPULL}.json', 
                  Body=json_text)

    # Break when no articles left
    if news_pull['articles'] == []:
        break

# Logging
logging.exception('')
print(f'Start pull: {STARTPULL}')
print(f'End pull: {ENDPULL}')
print(f'Query term: {QUERYPULL}')
print(f'Stopped on page: {PAGEPULL}')
