import tweepy
import pandas as pd
from textblob import TextBlob
from django.utils import encoding
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--search_tw', type=str, help='Enter the string to be searched')
parser.add_argument('--max', type=int, help='Maximum number of tweets in the CSV file')
args = parser.parse_args()

# Replace with the appropriate values
consumer_key = '####'
consumer_secret = '####'
access_token = '####'
access_token_secret = '####'

max_size = args.max  # Maximum number of tweets in the CSV file
pos_sent_th = 0.3  # Threshold for positive tweets
neg_sent_th = -pos_sent_th  # Threshold for negative tweets
search = args.search_tw  # Change the string to get a csv file with a different search result
mat = np.array(['Statement', 'Sentiment'])  # numpy variable to store all the tweets
count = 1  # Used to count the number of tweets

# Setup tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        global count, mat  # Used so that we can change the values from the method

        # Find the Sentiment for the tweet
        analysis = TextBlob(status.text)

        # Set the Sent Variable to the appropriate value based on the sentiment polarity
        if analysis.sentiment.polarity > pos_sent_th:
            Sent = 'Positive'
        elif analysis.sentiment.polarity < neg_sent_th:
            Sent = 'Negative'
        else:
            return ''  # We don't want neutral tweets

        # Convert the unicode type of status.text value to string type
        tw = encoding.smart_str(status.text, encoding='ascii', errors='ignore')
        # Use only those tweets that containing the symbol @ in them
        if '@' in tw:
            tw = tw.split(':')  # Used to separate the user name
            if len(tw) > 1:
                mat = np.vstack([mat, [tw[1], Sent]])  # insert the tweet and the sentiment as a row to the mat variable
                count += 1  # Increment the count when the tweet is stacked

        # Check if the number of tweets have crossed the maximum value
        if count > max_size:
            df = pd.DataFrame(mat[1:], columns=[mat[0]])  # convert the numpy matrix to pandas dataframe
            df.to_csv('{}.csv'.format(search))  # save the dataframe as a csv file
            exit()


# used to get a continuous stream of tweets
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener, languages=["en"])
myStream.filter(track=['{}'.format(search)])
