// g++ -o iprocess iprocess.cpp -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -std=c++11

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <iostream>
#include <unistd.h>
#include <string>
#include <opencv2/opencv.hpp>
#include <sys/time.h>


using namespace cv;
using namespace std;


void process(Mat &img)
{
	// change s
	img.convertTo(img, CV_32FC3, 1.0/255);
	cvtColor(img, img, COLOR_BGR2HLS);
	
	int rows = img.rows;
	int cols = img.cols;
	int channels = img.channels();
	int step = img.step;
	step /= sizeof(float);
	float* data = (float*)img.data;
	for(int i=0;i<rows;i++)
		for(int j=0;j<cols;j++)
		{
			int pos = i*step + j*channels + 2;
			float res = data[pos] * 1.5;
			data[pos] = res > 1 ? 1 : res;
		}

	// threshold(img, img, 1, 1, THRESH_TRUNC);
	cvtColor(img, img, COLOR_HLS2BGR);
	img.convertTo(img, CV_8UC3, 255);

	// blur
	medianBlur(img, img, 5);
	GaussianBlur(img, img, Size(3,3), 1);
}


void read_and_write(string image_name)
{
	Mat img = imread(image_name);
	process(img);
	if (img.empty()) {
		cout << "Failed in processing image." << endl;
		return;
	}
	imwrite("test-c.bmp", img);
}


int main()
{
	string image_name = "./test.bmp";
	read_and_write(image_name);

	return 0;
}