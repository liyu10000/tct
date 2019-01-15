// g++ -o saturate saturate.cpp -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -std=c++11

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <dirent.h>
#include <bits/stdc++.h> 
#include <sys/stat.h> 
#include <sys/types.h> 

using namespace std;
using namespace cv;


int scanFiles(vector<string> &fileList, string inputDirectory)
{
    inputDirectory = inputDirectory.append("/");

    DIR *p_dir;
    const char* str = inputDirectory.c_str(); 
    p_dir = opendir(str); 
    if( p_dir == NULL) { 
	    cout<< "can't open :" << inputDirectory << endl; 
    }

	struct dirent *p_dirent; 
	while ( p_dirent = readdir(p_dir)) { 
		string tmpFileName = p_dirent->d_name; 
		if( tmpFileName == "." || tmpFileName == "..")
 		{
            continue;
        }
        else
		{
            fileList.push_back(tmpFileName);
        }
    }
	closedir(p_dir);
    return fileList.size();
}


double alpha = 1.9; /**< 控制对比度 */
int beta = -150;  /**< 控制亮度 */


int main( int argc, char** argv )
{
    if (argc <= 1) {
        cout << "need to pass directories as parameters" << endl;
        return -1;
    }

    string src_dir = argv[1];
    string dst_dir = argv[2];

    mkdir(dst_dir.c_str(), 0777);

    vector<string> filenames;
	int fn = scanFiles(filenames, src_dir);
	cout<<"# files: "<< filenames.size() <<endl;

	for(int i=0; i<fn; i++){
		Mat image = imread( src_dir + filenames[i] );
        // cout << src_dir + filenames[i] << " " << image.cols << " " << image.rows << endl;
		Mat new_image = Mat::zeros( image.size(), image.type() );

		/// 执行运算 new_image(i,j) = alpha*image(i,j) + beta
    	for( int y = 0; y < image.rows; y++ )
    	{
      	  	for( int x = 0; x < image.cols; x++ )
       	 	{
            	for( int c = 0; c < 3; c++ )
            	{
               		 new_image.at<Vec3b>(y,x)[c] = saturate_cast<uchar>( alpha*( image.at<Vec3b>(y,x)[c] ) + beta );
         	   	}
       		 }
   		 }
		imwrite(dst_dir + filenames[i], new_image);
        // cout << dst_dir + filenames[i] << endl;
        // imwrite(filenames[i], new_image);
	}

    /// 读入用户提供的图像
   

    /// 创建窗口
    // namedWindow("Original Image", 1);
    //namedWindow("New Image", 1);

    /// 显示图像
    // imshow("Original Image", image);
    //imshow("New Image", new_image);
	
    /// 等待用户按键
    // waitKey();
    cout<<"done"<<endl;
    return 0;
}
