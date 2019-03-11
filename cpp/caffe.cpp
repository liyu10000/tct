// g++ -g -Wall -o caffe caffe.cpp -L/usr/local/bin/ -lcaffe -I/usr/local/cuda/include -lboost_system -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11

#include <caffe/caffe.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iosfwd>
#include <memory>
#include <string>
#include <utility>
#include <vector>


using namespace cv;
using namespace std;
using namespace caffe;


typedef pair<string, float> Prediction;


// class Classifier {
// public:
// 	Classifier(const string& model_file, const string& trained_file, const string& label_file, int gpu);
// 	vector<Prediction> Classify(const Mat* img, int N = 5);

// private:
// 	vector<float> Predict(const Mat& img);
// 	void WrapInputLayer(vector<Mat>* input_channels);
// 	void Preprocess(Mat& img, vector<Mat>* input_channels);

// 	Net<float> net;
// 	Size input_geometry_;
// 	int num_channels_;
// 	vector<string> labels_;
// };


// Classifier::Classifier(const string& model_file, const string& trained_file, const string& label_file, int gpu) {
// 	// #ifdef CPU_ONLY
// 	//  	Caffe::set_mode(Caffe::CPU);
// 	// #else
// 	// 	Caffe::set_mode(Caffe::GPU);
// 	// #endif
// 	// Caffe::SetDevice(gpu);

// 	// net(model_file, TEST);
// 	// net.CopyTrainedLayersFrom(trained_file);
// 	// cout << "Loaded caffe model" << endl;

// }


int main(int argc, char** argv) {
	printf("Build Caffe ResNet50 Classifier\n");

	string model_file = "/home/hdd0/Develop/xxx/workflow/categorization/deploy.prototxt";
	string trained_file = "/home/hdd0/Develop/xxx/workflow/categorization/resnet50_iter_740000.caffemodel";
	string label_file = "/home/hdd0/Develop/xxx/workflow/categorization/labels.txt";
	int gpu = 0;

	// Classifier classifier(model_file, trained_file, label_file, gpu);

	Net<float> net(model_file, TEST);
	net.CopyTrainedLayersFrom(trained_file);
	cout << "Loaded caffe model" << endl;


	return 0;
}