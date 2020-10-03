import logging
import re
import pandas as pd
import json
from textblob import TextBlob
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
    response = s3.list_objects_v2(Bucket=S3BUCKETNAME, MaxKeys=5, Prefix=f'newsapi/pull/{DATE_PULLED}/{QUERY_PULLED}-')

    if response['ResponseMetadata']['HTTPStatusCode'] == 200 and response['KeyCount'] > 0:
        
        df_all = pd.DataFrame([])

        for item in range(response['KeyCount']):

            # Convert each page to dataframe
            key = response['Contents'][item]['Key']
            data = s3.get_object(Bucket=S3BUCKETNAME, Key=key)
            data = data['Body']
            data = json.load(data)
            data = data['articles']
            df = pd.json_normalize(data)
            df = df[['title','description','publishedAt']]

            # Clean title and description text
            df['title'] = df['title'].apply(lambda arg: ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", str(arg)).split()))
            df['description'] = df['description'].apply(lambda arg: ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", str(arg)).split()))

            # Get sentiments from title and description
            df['title_polarity'] = df['title'].apply(lambda arg: TextBlob(arg).sentiment.polarity)
            df['description_polarity'] = df['description'].apply(lambda arg: TextBlob(arg).sentiment.polarity)
            print(df.info(), df.head())
            print(f'SUCCESS: convert {key} from {S3BUCKETNAME} to dataframe')
            
            # Append pages together
            df_all = df_all.append(df)

    else:
        logging.exception('')
        print(response)

except:
    logging.exception('')
    print(response)
    quit()


# Output to local for great expectations testing
df_all.to_csv(f'./great_expectations/newsapi-pull-{DATE_PULLED}-{QUERY_PULLED}.csv', index=False)


# Final logging
logging.exception('')
print(df_all.info(), df_all.head())
