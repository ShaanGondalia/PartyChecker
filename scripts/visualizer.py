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
    PARTY_COLORS = {'All': 'purple', 'Democrat': 'blue', 'Republican': 'red'}
    FREQ_KEY = 'frequency'
    WORD_KEY = 'word'

    def __init__(self):
        tqdm.pandas()

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
        df_filtered = self._filter_words(cleaned_words, df)

        self._summary_statistics(df, cleaned_words, df_filtered, word_type)

        # Frequency of words in df
        freqs = self._get_word_frequency(cleaned_words, df_filtered)

        self._plot_top_n_words(freqs, ylabel=f'{word_type} Word')
        self._plot_count_by_party(df_filtered, ylabel=f'{word_type} Word Counts')
        self._plot_prop_by_party(df, df_filtered, ylabel=f'{word_type} Word Tweet Proportions')

        plt.show()

    def _summary_statistics(self, df, words, df_filtered, word_type):
        """ Generates some summary statistics about the dataset """
        count_filtered = df_filtered.groupby(self.PARTY_KEY)['tweet'].count()
        count_df = df.groupby(self.PARTY_KEY)['tweet'].count()
        print(f"Percentage of tweets with {word_type} words:")
        print(count_filtered/count_df)
        self._party_word_proportion(df, words, 'D', word_type)
        self._party_word_proportion(df, words, 'R', word_type)

    def _party_word_proportion(self, df, words, party, word_type):
        """ Generates the proportion of words in all words in tweets given party """
        party_mask = df['party'] == party

        #for w in tqdm(words):
        #    count += df[party_mask][self.TOKEN_KEY].apply(lambda x: x.count(w)).sum()
        count = words.progress_apply(lambda w: df[party_mask][self.TOKEN_KEY].apply(lambda x: x.count(w)).sum()).sum()
        total = df[party_mask][self.TOKEN_KEY].apply(lambda x: len(x)).sum()
        prop = count / total
        print(f'Proportion of {word_type} words in {party} tweets: {prop}')

    def _process_words(self, words):
        """ Remove non-alphanumeric words """
        return words[words.str.isalnum()]

    def _filter_words(self, words, df):
        """ Returns a new df with entries that contain a word in words """
        print("Filtering tweets that don't contain given words:")
        mask = [False] * len(df.index)
        for w in tqdm(words):
            mask = mask | df[self.TOKEN_KEY].apply(lambda x: w in x)
        return df[mask]

    def _get_word_frequency(self, words, df):
        """ Gets the frequency of words in df for every word in word_arr """
        print("Generating word frequencies:")
        freqs = words.to_frame(name=self.WORD_KEY)
        freqs['Democrat'] = words.progress_apply(
            lambda word: self._freq_of_word_by_party(word, df, 'D'))
        freqs['Republican'] = words.progress_apply(
            lambda word: self._freq_of_word_by_party(word, df, 'R'))
        freqs['Total'] = freqs['Democrat'] + freqs['Republican']
        return freqs

    def _freq_of_word_by_party(self, word, df, party):
        """ Gets frequency of word by party """
        party_mask = df[self.PARTY_KEY] == party
        return df[party_mask][self.TOKEN_KEY].apply(lambda x: x.count(word)).sum()

    def _plot_top_n_words(self, freqs, n=10, ylabel='Word'):
        top = freqs.nlargest(n, 'Total')
        top = top.set_index(self.WORD_KEY)
        top[['Democrat', 'Republican']].plot.barh(stacked=True, color=['blue', 'red', 'purple'])
        plt.ylabel(ylabel)

    def _plot_count_by_party(self, df, ylabel='Tweet Count'):
        """ Plots the count of tweets in the df by party """
        counts_party = df.groupby(self.PARTY_KEY)['tweet'].count().reset_index()
        p = sns.catplot(data=counts_party, x=self.PARTY_KEY, y='tweet', kind='bar', color='gray',
                        palette=sns.color_palette(['blue', 'red']))
        p.set_axis_labels('Party', ylabel)

    def _plot_prop_by_party(self, df, df_words, ylabel='Tweet Proportion'):
        """ Plots the proportion of tweets between two dataframes by party """
        counts_party = df_words.groupby(self.PARTY_KEY)['tweet'].count().reset_index()
        total_counts_party = df.groupby(self.PARTY_KEY)['tweet'].count().reset_index()
        counts_party['props'] = counts_party['tweet'].divide(total_counts_party['tweet'])
        p = sns.catplot(data=counts_party, x=self.PARTY_KEY, y='props', kind='bar', color='gray',
                        palette=sns.color_palette(['blue', 'red']))
        p.set_axis_labels('Party', ylabel)

    def _visualize_party_words(self, df, party='All'):
        """ Visualizes all words used by party members """
        tokens = np.concatenate(df[self.TOKEN_KEY].values)
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
