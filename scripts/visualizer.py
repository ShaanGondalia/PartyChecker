from wordcloud import WordCloud
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
%matlpotlib inline


class Visualizer():

    PARTY_KEY = 'party'
    TOKEN_KEY = 'tokens_no_stop'
    PARTY_COLORS = {'All': 'purple', 'Democrat': 'blue', 'Republican': 'red'}

    def visualize_words(self, df):
        dems = df[df[self.PARTY_KEY] == 'D']
        reps = df[df[self.PARTY_KEY] == 'R']

        self._visualize_party_words(df)
        self._visualize_party_words(df, party='Democrat')
        self._visualize_party_words(df, party='Republican')

        plt.show()

    def _visualize_party_words(self, df, party='ALL'):
        """ Visualizes all words used by party members """
        tokens = np.concatenate(df[self.TOKEN_KEY].values)
        self._create_word_cloud(tokens, party)
        self._visualize_value_counts(tokens, party)

    def _create_word_cloud(self, tokens, party):
        """ Creates a word cloud from the given tokens """
        words_for_cloud = " ".join(tokens)+" "
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
