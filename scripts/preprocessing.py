import warnings
import pandas as pd
import numpy as np
import re
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
# warnings.filterwarnings("ignore", category=DeprecationWarning)


class PreProcessor():

    TIDY_TWEET = 'tidy_tweet'

    def __init__(self):
        nltk.download('stopwords')

    def pre_process_df(self, df):
        df[self.TIDY_TWEET] = df['tweet'].str.lower()
        # REMOVE '@USER'
        print('Removing users from Tweets')
        df[self.TIDY_TWEET] = np.vectorize(self._remove_users)(
            df[self.TIDY_TWEET], "@ [\w]*", "@[\w]*")
        # REMOVE HASHTAGS
        print('Removing hashtags from Tweets')
        df[self.TIDY_TWEET] = np.vectorize(self._remove_hashtags)(
            df[self.TIDY_TWEET], "# [\w]*", "#[\w]*")
        # REMOVE LINKS
        print('Removing links from Tweets')
        df[self.TIDY_TWEET] = np.vectorize(self._remove_links)(df[self.TIDY_TWEET])
        # EXTRACT TWEET DATE
        print('Extracting Tweet dates')
        df['date'] = df['tweet'].str.extract(r"([A-Z][a-z]+\s\d+,\s\d+)\s*$")
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # REMOVE Punctuations, Numbers, and Special Characters
        print('Removing punctuation, numbers, and special characters from Tweets')
        df[self.TIDY_TWEET] = df[self.TIDY_TWEET].str.replace("[^a-zA-Z#]", " ", regex=True)
        # TOKENIZATION
        print('Tokenizing Tweets')
        df['tidy_tweet_tokens'] = list(self._tokenize(df[self.TIDY_TWEET]))
        # REMOVE STOPWORDS
        print('Removing stop words from Tweets')
        df['tokens_no_stop'] = self._remove_stopwords(df['tidy_tweet_tokens'])
        # DROP EMPTY TWEETS
        print('Dropping empty Tweets')
        df = df[df['tokens_no_stop'].apply(lambda x: len(x)) > 0]
        print('Done processing Tweets!')
        return df

    def _remove_users(self, tweet, pattern1, pattern2):
        r = re.findall(pattern1, tweet)
        for i in r:
            tweet = re.sub(i, '', tweet)

        r = re.findall(pattern2, tweet)
        for i in r:
            tweet = re.sub(i, '', tweet)
        return tweet

    def _remove_hashtags(self, tweet, pattern1, pattern2):
        r = re.findall(pattern1, tweet)
        for i in r:
            tweet = re.sub(i, '', tweet)
        r = re.findall(pattern2, tweet)
        for i in r:
            tweet = re.sub(i, '', tweet)
        return tweet

    def _remove_links(self, tweet):
        tweet_no_link = re.sub(r"http\S+", "", tweet)
        return tweet_no_link

    def _tokenize(self, tweet):
        for word in tweet:
            yield(simple_preprocess(str(word), deacc=True))

    def _remove_stopwords(self, tweets):
        # Prepare Stop Words
        stop_words = stopwords.words('english')
        stop_words.extend(['from', 'https', 'twitter', 'religions', 'pic',
                           'twitt', 'today', 'will', 'thank', 'thanks',
                           'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                           'aug', 'sep', 'oct', 'nov', 'dec', 'great', 'new', 'day', 'rt',
                           'th', 'morning', 'week', 'com', 'net'])
        # words to remove from stopwords
        remove_words = ['we', 'our', 'ours', 'ourselves']
        stop_words = [e for e in stop_words if e not in remove_words]
        return [[word for word in simple_preprocess(str(tweet)) if word not in stop_words] for tweet in tweets]
