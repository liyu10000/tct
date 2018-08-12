#%matplotlib inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from pandas import read_csv
from datetime import datetime
from sklearn import datasets, linear_model
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from feature_importances import plot_feature_importances
from xgboost import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
# load data
dataset = read_csv('unlabeled_0812.csv', index_col=0)
# mark all NA values with 0
dataset.fillna(0, inplace=True)
# drop the first 24 hours
dataset = dataset
# summarize first 5 rows
print(dataset.head(5))
# save to file
dataset.to_csv('jnj2.csv')

clf = XGBClassifier()

xtitles = [
    'ASCUS_s','LSIL_s','ASCH_s','HSIL_s','SCC_s','ASCUS_s_005','LSIL_s_005','ASCH_s_005','HSIL_s_005',\
    'SCC_s_005','ASCUS_s_01','LSIL_s_01','ASCH_s_01','HSIL_s_01','SCC_s_01','ASCUS_s_02','LSIL_s_02','ASCH_s_02',\
    'HSIL_s_02','SCC_s_02','ASCUS_s_03','LSIL_s_03','ASCH_s_03','HSIL_s_03','SCC_s_03','ASCUS_s_04','LSIL_s_04',\
    'ASCH_s_04','HSIL_s_04','SCC_s_04',	'ASCUS_s_05','LSIL_s_05','ASCH_s_05','HSIL_s_05','SCC_s_05','ASCUS_s_06',\
    'LSIL_s_06','ASCH_s_06','HSIL_s_06','SCC_s_06','ASCUS_s_07','LSIL_s_07','ASCH_s_07','HSIL_s_07','SCC_s_07',\
    'ASCUS_s_08','LSIL_s_08','ASCH_s_08','HSIL_s_08','SCC_s_08','ASCUS_s_09','LSIL_s_09','ASCH_s_09','HSIL_s_09',\
    'SCC_s_09', 'ASCUS_s_099','LSIL_s_099','ASCH_s_099','HSIL_s_099','SCC_s_099','ASCUS_c','LSIL_c','ASCH_c','HSIL_c',\
    'SCC_c','ASCUS_c_01','LSIL_c_01','ASCH_c_01','HSIL_c_01','SCC_c_01','ASCUS_c_02','LSIL_c_02','ASCH_c_02',\
    'HSIL_c_02','SCC_c_02','ASCUS_c_03','LSIL_c_03','ASCH_c_03','HSIL_c_03','SCC_c_03','ASCUS_c_04','LSIL_c_04',\
    'ASCH_c_04','HSIL_c_04','SCC_c_04','ASCUS_c_05','LSIL_c_05','ASCH_c_05','HSIL_c_05','SCC_c_05','ASCUS_c_06',\
    'LSIL_c_06','ASCH_c_06','HSIL_c_06','SCC_c_06','ASCUS_c_07','LSIL_c_07','ASCH_c_07','HSIL_c_07','SCC_c_07',\
    'ASCUS_c_08','LSIL_c_08','ASCH_c_08','HSIL_c_08','SCC_c_08','ASCUS_c_09','LSIL_c_09','ASCH_c_09','HSIL_c_09',\
    'SCC_c_09','ASCUS_c_099','LSIL_c_099','ASCH_c_099','HSIL_c_099','SCC_c_099','ASCUS_c_0999','LSIL_c_0999',\
    'ASCH_c_0999','HSIL_c_0999','SCC_c_0999','w_mean','h_mean','v_mean','w_01','w_02','w_03','w_04','w_05','w_06',\
    'w_07','w_08','w_09','h_01','h_02','h_03','h_04','h_05','h_06','h_07','h_08','h_09','d_01','d_02','d_03','d_04','d_05',\
    'd_06','d_07','d_08','d_09','v_01','v_02','v_03','v_04','v_05','v_06','v_07','v_08','v_09']

X = dataset[xtitles]
y = dataset[['class_i']]

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=2018)
# predict
def plot_predict(modelname, x_test, y_test, figsize=(8,8)):  
    clf = joblib.load(modelname) 
    # score = clf.score(x_test, y_test)
    
    y_pred = clf.predict(x_test)
    score = clf.score(x_test, y_test)
    print ('score=',clf.score(y_test,y_pred))

          
    plt.figure()
    plt.plot(x_test.values[:,0], y_test,'go',label='True value')
    plt.plot(x_test.values[:,0], y_pred,'ro',label='Predict value')
    plt.title(clf.__class__.__name__+'-score: %f'%score)
    plt.xlabel('Run time (days)')
    plt.ylabel('Titer (g/L)')
    plt.legend()
    plt.savefig(modelname+"predict.png")
    

    plt.show()

# 测试集，画图对预测值和实际值进行比较
def test_validate(x_test, y_test, y_predict, classifier):
    
    x = range(len(y_test))
    plt.plot(x, y_test, "ro", markersize=5, zorder=3, label=u"true_v")
    plt.plot(x, y_predict, "go", markersize=8, zorder=2, label=u"predict_v,$R^2$=%.3f" % classifier.score(x_test, y_test))
    plt.legend(loc="upper left")
    plt.xlabel("number")
    plt.ylabel("true?")
    plt.show()
def confusion_accuracy(x_test, y_true, clf):
    y_pred = clf.predict(x_test)
    
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_true=y_true, y_pred=y_pred)
    
    from sklearn.metrics import classification_report
    cr = classification_report(y_true=y_true, y_pred=y_pred)

    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y_true=y_true, y_pred=y_pred)
    
    print('Model name:', clf.__class__.__name__)
    print(clf.__class__.__name__+' confusion_matrix:', cm)
    print(clf.__class__.__name__+' classification_report', cr)
    print(clf.__class__.__name__+' classification_report', acc)

feat_imp = plot_feature_importances(clf, x_train, y_train, top_n=x_train.shape[1], title=clf.__class__.__name__)
clf.fit(x_train, y_train)
modelname = clf.__class__.__name__+'.pkl'
joblib.dump(clf, modelname)
print(feat_imp)
# 绘制测试集结果验证
y_pred = clf.predict(x_test)
confusion_accuracy(x_test, y_test, clf)
print(confusion_accuracy)
