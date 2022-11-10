from wordcloud import WordCloud
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


class Visualizer():

    PARTY_KEY = 'party'
    TOKEN_KEY = 'tokens_no_stop'
    TOKEN_WITH_STOP_KEY = 'tidy_tweet_tokens'
    TIDY_KEY = 'tidy_tweet'
    PARTY_COLORS = {'All': 'purple', 'Democrat': 'blue', 'Republican': 'red'}
    FREQ_KEY = 'frequency'
    WORD_KEY = 'word'

    def visualize_words(self, df):
        dems = df[df[self.PARTY_KEY] == 'D']
        reps = df[df[self.PARTY_KEY] == 'R']

        self._visualize_party_words(df)
        self._visualize_party_words(df, party='Democrat')
        self._visualize_party_words(df, party='Republican')

        plt.show()

    def visualize_word_freq(self, words, df, word_type='Negative'):
        """Visualizes the frequency of specified words in the dataframe. 

        Args:
            words: A series of words to search for
            df: The dataframe to analyze
            word_type: Qualifier for the word type used in visualizations
        """
        cleaned_words = self._process_words(words)
        df_words = self._filter_words(cleaned_words, df)
        # Frequency of words in df
        freq_map = self._get_word_frequency(cleaned_words, df_words)
        word_freqs = pd.DataFrame(
            list(zip(freq_map.keys(), freq_map.values())), columns=[self.WORD_KEY, self.FREQ_KEY])

        self._plot_top_ten_words(word_freqs, ylabel=f'{word_type} Word')
        self._plot_count_by_party(df_words, ylabel=f'{word_type} Word Counts')

        plt.show()

    def _process_words(self, words):
        """ Remove non-alphanumeric words """
        return words[words.str.isalnum()]

    def _filter_words(self, words, df):
        """ Returns a new df with entries that contain a word in words """
        print("Filtering tweets that don't contain given words:")
        mask = [False] * len(df.index)
        for w in tqdm(words):
            mask = mask | df[self.TOKEN_WITH_STOP_KEY].apply(lambda x: w in x)
        return df[mask]

    def _get_word_frequency(self, words, df):
        """ Gets the frequency of words in df for every word in word_arr """
        dic = {}
        print("Generating word frequencies:")
        for w in tqdm(words):
            dic[w] = df[self.TOKEN_WITH_STOP_KEY].apply(lambda x: x.count(w)).sum()
        return dic

    def _plot_top_ten_words(self, word_freqs, ylabel='Word'):
        top_ten = word_freqs.nlargest(10, self.FREQ_KEY)
        p = sns.catplot(data=top_ten, x=self.FREQ_KEY, y=self.WORD_KEY, kind='bar', color='gray')
        p.set(ylabel=ylabel)

    def _plot_count_by_party(self, df, ylabel='Tweet Count'):
        """ Plots the count of tweets in the df by party """
        counts_party = df.groupby(self.PARTY_KEY)['tweet'].count().reset_index()
        p = sns.catplot(data=counts_party, x=self.PARTY_KEY, y='tweet', kind='bar', color='gray',
                        palette=sns.color_palette(['blue', 'red']))
        p.set_axis_labels('Party', ylabel)

    def _visualize_party_words(self, df, party='All'):
        """ Visualizes all words used by party members """
        tokens = np.concatenate(df[self.TOKEN_KEY
].values)
        self._create_word_cloud(tokens, party)
        self._visualize_value_counts(tokens, party)

    def _create_word_cloud(self, tokens, party):
        """ Creates a word cloud from the given tokens """
        words_for_cloud = ' '.join(tokens)+' '
        wordcloud = WordCloud(width=800, height=800,
                              background_color='white',
                              min_font_size=10).generate(words_for_cloud)
        plt.figure(figsize=(4, 4), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.title(f'{party} Tweets Word Cloud', fontsize=20)

    def _visualize_value_counts(self, tokens, party):
        """ Visualize the most common words used by party members """
        value_counts = pd.Series(list(tokens)).value_counts()
        value_counts = value_counts[value_counts > 1]
        value_counts = value_counts[value_counts > value_counts.quantile(0.995)]

        plt.figure(figsize=(5, len(value_counts)//5), facecolor=None)
        plt.title(f'{party} Value Counts')
        sns.barplot(x=value_counts.values, y=value_counts.index, color=self.PARTY_COLORS[party])
