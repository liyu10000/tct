from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
#from sklearn.feature_extraction.text import TfidfTransformer
from pandas import read_csv
from sklearn.externals import joblib
from xgboost import XGBClassifier

pkl_file = "XGBClassifier1200.pkl"
classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]

def xgboost_predict(csv_file):
    dataset = read_csv(csv_file, index_col=0)
    # xtitles = [
    #     'ASCUS_s','LSIL_s','ASCH_s','HSIL_s','SCC_s','ASCUS_s_005','LSIL_s_005','ASCH_s_005','HSIL_s_005',
    #     'SCC_s_005','ASCUS_s_01','LSIL_s_01','ASCH_s_01','HSIL_s_01','SCC_s_01','ASCUS_s_02','LSIL_s_02','ASCH_s_02',
    #     'HSIL_s_02','SCC_s_02','ASCUS_s_03','LSIL_s_03','ASCH_s_03','HSIL_s_03','SCC_s_03','ASCUS_s_04','LSIL_s_04',
    #     'ASCH_s_04','HSIL_s_04','SCC_s_04',	'ASCUS_s_05','LSIL_s_05','ASCH_s_05','HSIL_s_05','SCC_s_05','ASCUS_s_06',
    #     'LSIL_s_06','ASCH_s_06','HSIL_s_06','SCC_s_06','ASCUS_s_07','LSIL_s_07','ASCH_s_07','HSIL_s_07','SCC_s_07',
    #     'ASCUS_s_08','LSIL_s_08','ASCH_s_08','HSIL_s_08','SCC_s_08','ASCUS_s_09','LSIL_s_09','ASCH_s_09','HSIL_s_09',
    #     'SCC_s_09', 'ASCUS_s_099','LSIL_s_099','ASCH_s_099','HSIL_s_099','SCC_s_099','ASCUS_c','LSIL_c','ASCH_c','HSIL_c',
    #     'SCC_c','ASCUS_c_01','LSIL_c_01','ASCH_c_01','HSIL_c_01','SCC_c_01','ASCUS_c_02','LSIL_c_02','ASCH_c_02',
    #     'HSIL_c_02','SCC_c_02','ASCUS_c_03','LSIL_c_03','ASCH_c_03','HSIL_c_03','SCC_c_03','ASCUS_c_04','LSIL_c_04',
    #     'ASCH_c_04','HSIL_c_04','SCC_c_04','ASCUS_c_05','LSIL_c_05','ASCH_c_05','HSIL_c_05','SCC_c_05','ASCUS_c_06',
    #     'LSIL_c_06','ASCH_c_06','HSIL_c_06','SCC_c_06','ASCUS_c_07','LSIL_c_07','ASCH_c_07','HSIL_c_07','SCC_c_07',
    #     'ASCUS_c_08','LSIL_c_08','ASCH_c_08','HSIL_c_08','SCC_c_08','ASCUS_c_09','LSIL_c_09','ASCH_c_09','HSIL_c_09',
    #     'SCC_c_09','ASCUS_c_099','LSIL_c_099','ASCH_c_099','HSIL_c_099','SCC_c_099','ASCUS_c_0999','LSIL_c_0999',
    #     'ASCH_c_0999','HSIL_c_0999','SCC_c_0999','w_mean','h_mean','v_mean','w_01','w_02','w_03','w_04','w_05','w_06',
    #     'w_07','w_08','w_09','h_01','h_02','h_03','h_04','h_05','h_06','h_07','h_08','h_09','d_01','d_02','d_03','d_04','d_05',
    #     'd_06','d_07','d_08','d_09','v_01','v_02','v_03','v_04','v_05','v_06','v_07','v_08','v_09']
    # X = dataset[xtitles]
    # y = dataset[['class_i']]
    X = dataset.iloc[:,1:]
    y = dataset.iloc[:,0]
    x_test = X
    y_test = y
    with open(pkl_file, 'rb') as f:
        model = joblib.load(f)
    def confusion_accuracy(x_test, y_true, model):
        y_pred = model.predict(x_test)
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true=y_true, y_pred=y_pred)
        from sklearn.metrics import classification_report
        cr = classification_report(y_true=y_true, y_pred=y_pred)
        from sklearn.metrics import accuracy_score
        acc = accuracy_score(y_true=y_true, y_pred=y_pred)
        print('Model name:', model.__class__.__name__)
        print(model.__class__.__name__+' confusion_matrix:')
        print(cm)
        print(model.__class__.__name__+' classification_report')
        print(cr)
        print(model.__class__.__name__+' classification_report: predict {}, accuracy {}'.format(classes[y_pred[0]], acc))
        return classes[y_pred[0]]
    return confusion_accuracy(x_test, y_test, model)


if __name__ == "__main__":
    xgboost_predict('2018-03-15-14_54_10_c2_f.csv')