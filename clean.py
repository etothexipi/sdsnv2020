import logging
import pandas as pd
import json
from datetime import datetime, timedelta
import io
import boto3
import os



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



# Get raw data from pull.py output
try:
    response = s3.list_objects_v2(Bucket=S3BUCKETNAME, MaxKeys=1000, Prefix=f'newsapi/pull/{DATE_PULLED}/{QUERY_PULLED}-')

    if response['ResponseMetadata']['HTTPStatusCode'] == 200 and response['KeyCount'] > 0:
        
        for item in range(response['KeyCount']):

            # Convert each page to dataframe
            key = response['Contents'][item]['Key']
            data = s3.get_object(Bucket=S3BUCKETNAME, Key=key)
            data = data['Body']
            data = json.load(data)
            data = data['articles']
            df = pd.json_normalize(data)
            print(df.info(), df.head())
            print(f'SUCCESS: convert {key} from {S3BUCKETNAME} to dataframe')

    else:
        logging.exception('')
        print(response)

except:
    logging.exception('')
    print(response)
    quit()


# Final logging
logging.exception('')
print(f'Start pull: {DATE_PULLED}')
print(f'Query term: {QUERY_PULLED}')
