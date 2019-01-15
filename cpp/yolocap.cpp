// g++ -g -Wall -o yolocap yolocap.cpp libdarknet.so -ldl

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

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


int main(int argc, char **argv) {

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


	// detection
	char *image_name = (char *)"/home/hdd0/Develop/tct/cpp/20000_20000.bmp";
	detect(net, meta, image_name);


	close_lib();

	return 0;
}