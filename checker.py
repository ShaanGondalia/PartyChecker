import requests
import json
import pandas as pd
from secrets import BEARER_TOKEN


class Checker():

    USER_ID_ENDPOINT = 'https://api.twitter.com/2/users/by?usernames={}&user.fields=id'
    TIMELINE_ENDPOINT = 'https://api.twitter.com/2/users/{}/tweets'
    RETWEET_REGEX = r'RT @[A-Za-z0-9_]{1,15}: '
    APPLICATION_NAME = 'party-checker'

    def check(self, username):
        """ Uses summary statistics to check a user's political party """
        ids = self._lookup_user_ids(username)
        tweets = self._retrieve_tweets(ids[username.lower()])
        # TODO: Calculate summary statistics to check party affiliation


        print(tweets.head(10))

    def check_batch(self, usernames):
        ids = self._lookup_user_ids(username)
        for username in usernames:
            tweets = self._retrieve_tweets(ids[username.lower()])
        return None

    def _lookup_user_ids(self, usernames):
        """ Retrieves user ids for a list of usernames (twitter handles).
        Returns a map from username to user id """
        print(f'Looking up user ids for user: {usernames}')
        url = self.USER_ID_ENDPOINT.format(usernames)
        response = self._connect_to_endpoint(url)
        data = response['data']
        ids = {}
        for user in data:
            ids[user['username'].lower()] = user['id']
        return ids

    def _retrieve_tweets(self, user_id, num_tweets=100):
        """ Retrieves a dataframe of tweets from a user id """
        print(f'Retrieving tweets for user id: {user_id}')
        url = self.TIMELINE_ENDPOINT.format(user_id)
        params = self._get_timeline_params(num_tweets)
        response = self._connect_to_endpoint(url, params=params)
        tweets = pd.DataFrame(response['data'], columns=['text'])
        self._process_retweets(tweets)

        return tweets

    def _process_retweets(self, df):
        """Processes retweets, marking them with an additional column and 
        removing retweet prefix text.
        New columns:
            retweet: 1 if tweet is a retweet, 0 if not
        """
        df['retweet'] = df['text'].str.match(self.RETWEET_REGEX).astype(int)   
        df['text'] = df['text'].str.replace(self.RETWEET_REGEX, '', regex=True)

    def _get_timeline_params(self, num_tweets):
        params = {}
        params['tweet.fields'] = 'text'
        params['max_results'] = num_tweets
        return params

    def _connect_to_endpoint(self, url, params=None):
        """ Sends a request to an HTTP endpoint. Returns the response. """
        response = requests.request("GET", url, auth=self._bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Request returned an error: {response.status_code} {response.text}")
        return response.json()

    def _bearer_oauth(self, request):
        request.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
        request.headers["User-Agent"] = self.APPLICATION_NAME
        return request


def main():
    checker = Checker()
    checker.check("twitter")


if __name__ == '__main__':
    main()
