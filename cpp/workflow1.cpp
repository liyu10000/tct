// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0`
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11 -lboost_filesystem -lboost_system
// g++ -g -Wall -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11 -lboost_filesystem -lboost_system libdarknet.so -ldl

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vector>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>
#include <assert.h>
#include <glib.h>
#include <sys/time.h>
#include <mutex>
#include <queue>
#include <thread>
#include <condition_variable>

#include <opencv2/opencv.hpp>
#include "openslide.h"
// #include "openslide-common.h"


using namespace cv;
using namespace std;


struct network;
typedef struct network network;

typedef struct{
    int classes;
    char **names;
} metadata;

typedef struct {
    int w;
    int h;
    int c;
    float *data;
} image;

typedef struct{
    float x, y, w, h;
} box;

typedef struct detection{
    box bbox;
    int classes;
    float *prob;
    float *mask;
    float objectness;
    int sort_class;
} detection;


// int network_width(network *net);
int (*network_width)(network *net);

// int network_height(network *net);
int (*network_height)(network *net);

// network *net = load_network(char *cfg, char *weights, int clear);
network* (*load_network)(char *cfg, char *weights, int clear);

// float *predictions = network_predict(network net, float *X);
float* (*network_predict)(network net, float *X);

// metadata get_metadata(char *file);
metadata (*get_metadata)(char *file);

// image load_image(char *filename, int w, int h, int c);
// image load_image_color(char *filename, int w, int h);
image (*load_image_color)(char *filename, int w, int h);

// float *network_predict_image(network *net, image im);
float* (*network_predict_image)(network *net, image im);

// detection *get_network_boxes(network *net, int w, int h, float thresh, float hier_thresh, int *map, int relative, int *num);
detection* (*get_network_boxes)(network *net, int w, int h, float thresh, float hier_thresh, int *map, int relative, int *num);

// void do_nms_obj(detection *dets, int total, int classes, float thresh);
void (*do_nms_obj)(detection *dets, int total, int classes, float thresh);

// void free_image(image im);
void (*free_image)(image im);

// void free_detections(detection *dets, int n);
void (*free_detections)(detection *dets, int n);

// image make_image(int w, int h, int c);
image (*make_image)(int w, int h, int c);


void* handle = nullptr;

void open_lib(char *lib_name) {
  handle = dlopen(lib_name, RTLD_LAZY);
  if (!handle) {
    fprintf(stderr, "%s\n", dlerror());
    exit(1);
  }

  dlerror();  // clear any existing error
}


void close_lib() {
  dlclose(handle);
}


void load_functions() {
  network_width = (int (*)(network*)) dlsym(handle, "network_width");

  network_height = (int (*)(network*)) dlsym(handle, "network_height");

  load_network = (network* (*)(char*, char*, int)) dlsym(handle, "load_network");

  network_predict = (float* (*)(network, float*)) dlsym(handle, "network_predict");

  get_metadata = (metadata (*)(char*)) dlsym(handle, "get_metadata");

  load_image_color = (image (*)(char*, int, int)) dlsym(handle, "load_image_color");

  network_predict_image = (float* (*)(network*, image)) dlsym(handle, "network_predict_image");

  get_network_boxes = (detection* (*)(network*, int, int, float, float, int*, int, int*)) dlsym(handle, "get_network_boxes");

  do_nms_obj = (void (*)(detection*, int, int, float)) dlsym(handle, "do_nms_obj");

  free_image = (void (*)(image)) dlsym(handle, "free_image");

  free_detections = (void (*)(detection*, int)) dlsym(handle, "free_detections");

  make_image = (image (*)(int, int, int)) dlsym(handle, "make_image");
}


void detect(network *net, metadata meta, char *image_name) {
  // char *image_name = (char *)"/home/hdd0/Develop/xxx/gen608/2017-09-07-09_24_10_x18891_y23547_r0.bmp";
  float thresh = 0.5;
  float hier_thresh = 0.5;
  float nms = 0.45;

  image im = load_image_color(image_name, 0, 0);
  int num;
  network_predict_image(net, im);
  detection *dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, nullptr, 0, &num);
  do_nms_obj(dets, num, meta.classes, nms);

  // print detections
  for (int j = 0; j < num; j++) {
    for (int i = 0; i < meta.classes; i++) {
      if (dets[j].prob[i] > .0) {
        printf("%s, probability %f, objectness %f ", meta.names[i], dets[j].prob[i], dets[j].objectness);
        printf("(%f, %f, %f, %f)\n", dets[j].bbox.x, dets[j].bbox.y, dets[j].bbox.w, dets[j].bbox.h);
      }
    }
  }

  free_image(im);
  free_detections(dets, num);
}




static void read_region_and_half_size(openslide_t* osr, int64_t x, int64_t y, int64_t w, int64_t h, string save_path) {
	// openslide_t* osr = openslide_open(slide_name);

	uint32_t *buf = (uint32_t *) g_slice_alloc(w * h * 4);
	openslide_read_region(osr, buf, x, y, 0, w, h);

	Mat img(h, w, CV_8UC4, buf);
	cvtColor(img, img, CV_RGBA2RGB);
	pyrDown(img, img);
	imwrite(save_path + "/" + to_string(x) + "_" + to_string(y) + ".bmp", img);

	g_slice_free1(w * h * 4, buf);

	// openslide_close(osr);
}


// image ipl_to_image(IplImage* src)
// {
//     unsigned char *data = (unsigned char *)src->imageData;
//     int h = src->height;
//     int w = src->width;
//     int c = src->nChannels;
//     int step = src->widthStep;  // Size of aligned image row in bytes.
//     image out = make_image(w, h, c);
//     int i, j, k, count=0;;
//     #pragma parallel for 
//     for(k= 0; k < c; ++k){
//         for(i = 0; i < h; ++i){
//             for(j = 0; j < w; ++j){
//                 out.data[count++] = data[i*step + j*c + k]/255.; // Normalize
//             }
//         }
//     }
//     return out;
// }

// image mat_to_image(cv::Mat img_src)
// {
//     cv::Mat img;
//     imwrite("xxx.bmp", img_src);
//     cv::cvtColor(img_src, img, cv::COLOR_RGB2BGR);
//     IplImage imgTmp = img;
//     IplImage *input = cvCloneImage(&imgTmp);
//     return ipl_to_image(input);
// }


image mat_to_image(cv::Mat img_src)
{
    int h = img_src.rows;
    int w = img_src.cols;
    int c = img_src.channels();
    int step = img_src.step;
    image out = make_image(h, w, c);

    unsigned char *data = (unsigned char *)img_src.data;

    int i, j, k, count = 0;
    #pragma parallel for 
    for(k= 0; k < c; ++k){
        for(i = 0; i < h; ++i){
            for(j = 0; j < w; ++j){
                out.data[count++] = data[i*step + j*c + k]/255.; // Normalize
            }
        }
    }

    return out;
}


void read_region_and_detect(network *net, metadata meta, openslide_t* osr, int64_t x, int64_t y, int64_t w, int64_t h) {
  uint32_t *buf = (uint32_t *) g_slice_alloc(w * h * 4);
  openslide_read_region(osr, buf, x, y, 0, w, h);

  Mat img(h, w, CV_8UC4, buf);
  pyrDown(img, img);
  cvtColor(img, img, CV_RGBA2BGR);
  

  image im = mat_to_image(img);

  float thresh = 0.5;
  float hier_thresh = 0.5;
  float nms = 0.45;

  // image im = load_image_color("/home/hdd0/Develop/tct/cpp/20000_20000.bmp", 0, 0);
  int num;
  network_predict_image(net, im);
  detection *dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, nullptr, 0, &num);
  do_nms_obj(dets, num, meta.classes, nms);

  // print detections
  for (int j = 0; j < num; j++) {
    for (int i = 0; i < meta.classes; i++) {
      if (dets[j].prob[i] > .0) {
        printf("%s, probability %f, objectness %f ", meta.names[i], dets[j].prob[i], dets[j].objectness);
        printf("(%f, %f, %f, %f)\n", dets[j].bbox.x, dets[j].bbox.y, dets[j].bbox.w, dets[j].bbox.h);
      }
    }
  }

  // free_image(im);
  free_detections(dets, num);

  g_slice_free1(w * h * 4, buf);
}


static void print_downsamples(openslide_t *osr) {
	for (int32_t level = 0; level < openslide_get_level_count(osr); level++) {
		printf("level %d: downsample: %g\n",
			   level,
			   openslide_get_level_downsample(osr, level));
	}
}



int main(int argc, char** argv) {

  char * lib_name = (char *)"libdarknet.so";
  open_lib(lib_name);

  load_functions();


  char *cfgfile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.cfg";
  char *weightfile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.backup";
  network *net = load_network(cfgfile, weightfile, 0);

  int width = network_width(net);
  int height = network_height(net);
  cout << "net widthxheight: " << width << "x" << height << endl;

  char *metafile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.data";
  metadata meta = get_metadata(metafile);
  cout << "meta classes: " << meta.classes << endl;


  // // detection on local image
  // char *image_name = (char *)"/home/hdd0/Develop/tct/cpp/20000_20000.bmp";
  // detect(net, meta, image_name);
  // printf("finished detection\n");



  const char *slide_name = "/home/hdd0/Develop/tct/cpp/agc.tif";
  openslide_t* osr = openslide_open(slide_name);

  int64_t x = 20000;
  int64_t y = 20000;
  int64_t w = 1216;
  int64_t h = 1216;
  string save_path = "/home/hdd0/Develop/tct/cpp";

  // // cut image and save to local file
  // read_region_and_half_size(osr, x, y, w, h, save_path);
  // printf("finished cutting image\n");

  // read region and detect in memory
  read_region_and_detect(net, meta, osr, x, y, w, h);
  printf("finished read region and detection\n");

  openslide_close(osr);



  close_lib();


	return 0;
}