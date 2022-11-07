import pandas as pd
import csv
from tqdm import tqdm


class Converter():

    PARTIES = ['democrat', 'republican']
    CHAMBERS = ['house', 'senate']
    CONGRESSES = ['112', '113']
    DATA_FOLDER = 'data'
    RETWEET_REGEX = r'RT @[A-Za-z0-9_]{1,15}: '

    def convert(self):
        """Converts all data from all files into a single DataFrame.
        Columns:
            author: Tweet author (congress member)
            tweet: Raw tweet text
            party: D for Democrat, R for Republican
            chamber: H for House of Representatives, S for Senate
            congress: Session of congress (112 or 113)
        """
        dfs = []
        for party in self.PARTIES:
            for chamber in self.CHAMBERS:
                for congress in self.CONGRESSES:
                    dfs.append(self._convert_csv(party, chamber, congress))
        return pd.concat(dfs)

    def process_retweets(self, df):
        """Processes retweets, marking them with an additional column and 
        removing retweet prefix text.
        New columns:
            retweet: 1 if tweet is a retweet, 0 if not
        """
        df['retweet'] = df['tweet'].str.match(self.RETWEET_REGEX).astype(int)   
        df['tweet'] = df['tweet'].str.replace(self.RETWEET_REGEX, '', regex=True)

    def write_csv(self, df, fname="congress-tweets.csv"):
        """Writes a df to a csv file"""
        df.to_csv(f"{self.DATA_FOLDER}/{fname}", encoding='utf-8', index=False)

    def _convert_csv(self, party, chamber, congress):
        """Converts a single csv file to a dataframe"""
        fname = f"{self.DATA_FOLDER}/{party}-{chamber}-{congress}.csv"
        df_authors = pd.read_csv(fname, dtype=str)
        df_authors = df_authors.loc[:, ~
            df_authors.columns.str.contains('^Unnamed')]
        dfs = []
        for author in tqdm(df_authors.columns):
            tweets = df_authors[author]
            tweets = tweets.dropna()
            df_author = tweets.to_frame(name="tweet")
            df_author['author'] = author
            df_author['party'] = party[0].upper()
            df_author['chamber'] = chamber[0].upper()
            df_author['congress'] = congress
            dfs.append(df_author)
        return pd.concat(dfs)


def main():
    converter = Converter()
    df = converter.convert()
    converter.process_retweets(df)
    print(df.head())
    print(df.shape)
    converter.write_csv(df)


if __name__ == '__main__':
    main()
