import sys

import numpy as np
import sklearn
from sklearn import svm
from sklearn.externals import joblib

MODEL_EXIT = False


def train(path_data, path_label):
    X = np.loadtxt(path_data)
    y = np.loadtxt(path_label)
    clf = svm.SVC()
    clf.fit(X, y)
    joblib.dump(clf, 'algo.pkl')


def predict(X):
    clf = joblib.load('algo.pkl')
    res = clf.predict(X)
    return res[0]


if __name__ == '__main__':
    path_data = sys.argv[1]
    path_label = sys.argv[2]
    train(path_data, path_label)

    # X_test = np.loadtxt(path_data)
    # for i in range(np.shape(X_test)[0]):
    #     print(predict(X_test[i:i + 1]))
