import pandas as pd
import numpy as np
import re
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm


class PreProcessor():

    TIDY_TWEET = 'tidy_tweet'
    USER_REGEX = r'@ ?[\w]*'
    HASHTAG_REGEX = r'# ?[\w]*'
    LINK_REGEX = r'http\S+'
    DATE_REGEX = r'([A-Z][a-z]+\s\d+,\s\d+)\s*$'
    SPECIAL_CHAR_REGEX = r'[^a-zA-Z#]'

    def __init__(self):
        nltk.download('stopwords')
        tqdm.pandas()

    def pre_process_df(self, df):
        df[self.TIDY_TWEET] = self._tidify_tweet(df)
        df['date'] = self._extract_date(df)
        # TOKENIZATION
        print('Tokenizing Tweets')
        df['tidy_tweet_tokens'] = df[self.TIDY_TWEET].progress_apply(
            lambda tweet: simple_preprocess(tweet, deacc=True))
        # REMOVE STOPWORDS
        print('Removing stop words from Tweets')
        df['tokens_no_stop'] = self._remove_stopwords(df['tidy_tweet_tokens'])
        # DROP EMPTY TWEETS
        print('Dropping empty Tweets')
        df = df[df['tokens_no_stop'].progress_apply(lambda x: len(x)) > 0]
        print('Done processing Tweets!')
        return df

    def _tidify_tweet(self, df):
        lower = df['tweet'].str.lower()
        print('Removing users from Tweets')
        no_users = lower.str.replace(self.USER_REGEX, '', regex=True)
        print('Removing hashtags from Tweets')
        no_hashtags = no_users.str.replace(self.HASHTAG_REGEX, '', regex=True)
        print('Removing links from Tweets')
        no_links = no_hashtags.str.replace(self.LINK_REGEX, '', regex=True)
        print('Removing punctuation, numbers, and special characters from Tweets')
        return no_links.str.replace(self.SPECIAL_CHAR_REGEX, ' ', regex=True)

    def _extract_date(self, df):
        print('Extracting Tweet dates')
        date = df['tweet'].str.extract(self.DATE_REGEX).apply(str)
        return pd.to_datetime(date, errors='coerce')

    def _generate_stopwords(self):
        stop_words = stopwords.words('english')
        stop_words.extend(['from', 'https', 'twitter', 'religions', 'pic',
                           'twitt', 'today', 'will', 'thank', 'thanks',
                           'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                           'aug', 'sep', 'oct', 'nov', 'dec', 'great', 'new', 'day', 'rt',
                           'th', 'morning', 'week', 'com', 'net'])
        # words to remove from stopwords
        remove_words = ['my', 'i', 'mine', 'me', 'them', 'their',
                        'they', 'those', 'we', 'our', 'us', 'ourselves']
        return [e for e in stop_words if e not in remove_words]

    def _remove_stopwords(self, series):
        stop = self._generate_stopwords()
        return series.progress_apply(lambda tweet: [w for w in tweet if w not in stop])
