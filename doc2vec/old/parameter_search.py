from gensim.models import Doc2Vec
from multiprocessing import Pool
import smart_open
import os.path
import time
import glob
from gensim.test.test_doc2vec import ConcatenatedDoc2Vec
from contextlib import contextmanager
from collections import defaultdict
from collections import OrderedDict
from collections import namedtuple
from gensim.models import Doc2Vec
from IPython.display import HTML
from timeit import default_timer
import gensim.models.doc2vec
import multiprocessing
from os import remove
import numpy as np
import itertools
import datetime
import locale
import gensim
import sys
import re
from sklearn import linear_model
import fileinput
from sklearn.utils import shuffle
from sklearn import ensemble
from sklearn import svm
from sklearn.utils import resample
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn import svm
from sklearn.svm import SVC

### Grid Search Parameters ###
dirname = 'data_small'
models = [Doc2Vec.load('saved_doc2vec_models/Doc2Vec(dmc,d100,n5,w5,mc2,s0.001,t8)')]
classifier = SVC()
param_grid = [
  {'cache_size': [4000], 'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000], 'kernel': ['linear']},
  {'cache_size': [4000], 'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000], 'kernel': ['rbf']},
]
##############################

for model in models:
    print(model)

inferreds = [True, False]

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
num_lines_test = file_len(os.path.join(dirname, 'test-pos.txt'))
num_lines_test += file_len(os.path.join(dirname, 'test-neg.txt'))

SentimentDocument = namedtuple('SentimentDocument', 'words tags split sentiment')
def read_labeled_corpus(fpos, fneg, split):
    f_list = [fpos, fneg]
    i = 0
    for f in f_list:
        if i == 0:
            sentiment = 1.0
        else:
            sentiment = 0.0
        for line in open(f, encoding='utf-8'):
            tokens = gensim.utils.to_unicode(line).split()
            if(len(tokens)==0):
                continue
            words = tokens[1:]
            tags = [tokens[0]]
            yield SentimentDocument(gensim.utils.to_unicode(line).split()[1:], tags, split, sentiment)
        i+=1
        
#Error: 0.49597423510466987; Error Count: 22484; Test Count 45333; Predictor: SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
#          decision_function_shape=None, degree=3, gamma='auto', kernel='rbf',
#          max_iter=-1, probability=False, random_state=None, shrinking=True,
#          tol=0.001, verbose=False); Inferred: False
#          Doc2Vec(dm/c,d100,n5,w5,mc2,s0.001,t8)

test_model = models[0]
train_set = read_labeled_corpus(os.path.join(dirname, 'train-pos.txt'), os.path.join(dirname, 'train-neg.txt'), 'train')
train_targets, train_regressors = zip(*[(doc.sentiment, test_model.docvecs[doc.tags[0]]) for doc in train_set])
train_targets, train_regressors = shuffle(train_targets, train_regressors)

test_set = read_labeled_corpus(os.path.join(dirname, 'test-pos.txt'), os.path.join(dirname, 'test-neg.txt'), 'test')
test_targets, test_regressors = zip(*[(doc.sentiment, test_model.docvecs[doc.tags[0]]) for doc in test_set])    
test_targets, test_regressors = shuffle(test_targets, test_regressors)  

clf = RandomizedSearchCV(classifier, param_grid)
#clf = GridSearchCV(classifier, param_grid)
clf.fit(train_regressors, train_targets)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))