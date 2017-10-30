#!/usr/bin/env python3

# IMPORT TRAINING DATA
#================================================

import pandas as pd

# data for a given user:
#  * login times
#  * location(s) they've been employed at
#  * times they've logged hours for
#  

data = ('login_times', 'current_workplace')

training = pd.DataFrame(columns = data)


# TRAINING MODEL
#================================================

from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, KFold
