from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
import pandas as pd


class Classifier():

    TOKENS_KEY = 'tokens_no_stop'
    PARTY_KEY = 'party'

    def naive_bayes(self, df):
        data, label = self._get_data_from_df(df)
        train_data, test_data, train_label, test_label = self._get_data_from_df(data, label)
        nb_acc = self._classify_nb(train_data, train_label, test_data, test_label)
        base_acc = self._classify_dummy(train_data, train_label, test_data, test_label)

    def naive_bayes_feature_extraction(self, df):
        data, label = self._get_data_from_df(df)
        tf = TfidfVectorizer()
        text_tf = tf.fit_transform(data)
        train_data, test_data, train_label, test_label = self._split_data(text_tf, label)
        nb_acc = self._classify_nb(train_data, train_label, test_data, test_label)
        base_acc = self._classify_dummy(train_data, train_label, test_data, test_label)

    def _get_data_from_df(self, df):
        data = df[self.TOKENS_KEY].str.join(' ').values
        label = df[self.PARTY_KEY].values
        return data, label

    def _split_data(self, data, label):
        return train_test_split(data, label, test_size=0.3, random_state=2)

    def _classify_nb(train_data, train_label, test_data, test_label):
        nb_model = make_pipeline(CountVectorizer(binary=True), MultinomialNB())
        nb_model.fit(train_data, train_label)
        # float: test classification accuracy score of the model
        nb_acc nb_model.score(test_data, test_label)
        print("Naive Bayes test classification accuracy:", nb_acc)
        return nb_acc

    def _classify_dummy(train_data, train_label, test_data, test_label):
        dummy_clf = DummyClassifier(strategy='most_frequent')
        dummy_clf.fit(train_data, train_label)
        dummy_acc = dummy_clf.score(test_data, test_label)
        print("Baseline test classification accuracy:", dummy_acc)
        return dummy_acc
