from feature_extractor import FeatureExtractor
from predict_model import PredictModel



class ClassificationTreeStep():

    def __init__(self, gpus=[0,1,2,3]):
        self.gpus = gpus


    def load_models(self, feature_extract_weights=None, predict_weights=None):
        print("load models")

        # build feature extractor model
        self.class_feature_extrctor = FeatureExtrctor(gpu_num=len(self.gpus), gpus=','.join(self.gpus))
        self.class_feature_extrctor.build_model(feature_extract_weights)  # vgg19_finetune.h5

        # build predict model
        self.class_predict_model = PredictModel(gpu_num=len(self.gpus))
        self.class_predict_model.build_model()
        self.class_predict_model.load_weights(predict_weights)  # diagnosis.h5


    def prediction(self, img_path=None):
        print("prediction models")

        # extract feature
        res = class_feature_extrctor.read_big_pic(img_path)
        if res != 0:
            print("failed to read:", img_path)
            return
        feature = self.class_feature_extrctor.feature_extractor()

        # predict
        prediction = self.class_predict_model.predict(feature)

        # print prediction
        binary_classes = ["Normal", "Abnormal"]
        print("file name: {}, prediction: {}, probability: {}".format(img_path, binary_classes[np.argmax[prediction]], np.max(prediction)))


    def release_models(self):
        print("release models")

        del self.class_feature_extrctor
        del self.class_predict_model