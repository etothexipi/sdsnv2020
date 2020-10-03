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
if all(param in ['DATE_PULLED', 'QUERY_PULLED'] for param in os.environ) is True:
    DATE_PULLED = os.environ['DATE_PULLED']
    QUERY_PULLED = os.environ['QUERY_PULLED']

else:
    print(f'WARNING: Job params not all defined in environment. Running defaults')
    yesterday = datetime.today() + timedelta(days=-1)
    DATE_PULLED = yesterday.strftime('%Y-%m-%d')
    QUERY_PULLED = 'cryptocurrency'



# Get up to 5 pages of results for keyword by relevancy
for PAGEPULL in range(1,6):
    news_pull = newsapi.get_everything(
        q=QUERY_PULLED,
        from_param=DATE_PULLED,
        to=DATE_PULLED,
        language='en',
        sort_by='relevancy',
        page=PAGEPULL
    )

    # Break when no articles left
    if news_pull['articles'] == []:
        break

    # Put JSON as string to S3
    json_text = json.dumps(news_pull)
    object_key = f'newsapi/pull/{DATE_PULLED}/{QUERY_PULLED}-{PAGEPULL:04}.json'
    response = s3.put_object(Bucket=S3BUCKETNAME, Key=object_key, Body=json_text)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f'SUCCESS: Put {object_key} to {S3BUCKETNAME}')
    else:
        logging.exception('')
        print(response)
        quit()



# Final logging
logging.exception('')
print(f'Start pull: {DATE_PULLED}')
print(f'Query term: {QUERY_PULLED}')
print(f'Stopped on page: {PAGEPULL}')
