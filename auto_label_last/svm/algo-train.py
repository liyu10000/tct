import numpy as np
import sklearn
from sklearn import svm
from sklearn.externals import joblib
import os

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
    # path_data = 'train.txt'
    # path_label = 'label.txt'
    # train(path_data, path_label)

    path_data = "C:/tsimage/tct/auto_label_last/svm/train_test.txt"
    with open(path_data) as f:
        print(f.readlines())

    print(os.path.abspath(path_data))
    X_test = np.loadtxt(path_data)
    print(X_test)
    print(range(np.shape(X_test)[0]))
    for i in range(np.shape(X_test)[0]):
        print('-----', i)
        print(predict(X_test[i:i + 1]))
