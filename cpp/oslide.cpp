// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide
// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0`
// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>
#include <assert.h>
#include <glib.h>
#include <sys/time.h>

#include <opencv2/opencv.hpp>
#include "openslide.h"
// #include "openslide-common.h"

using namespace cv;
using namespace std;


static void print_downsamples(openslide_t *osr) {
	for (int32_t level = 0; level < openslide_get_level_count(osr); level++) {
		printf("level %d: downsample: %g\n",
			   level,
			   openslide_get_level_downsample(osr, level));
	}
}


static void test_read_region(openslide_t *osr) {
	int32_t level = 0;
	int64_t x = 10000, y = 10000, w = 608, h = 608;
	uint32_t *buf = (uint32_t *) g_slice_alloc(w * h * 4);
	openslide_read_region(osr, buf, x, y, level, w, h);

	Mat img(h, w, CV_8UC4, buf);
	cvtColor(img, img, CV_RGBA2RGB);
	imwrite("./test.bmp", img);

	g_slice_free1(w * h * 4, buf);
}


int main(int argc, char** argv) {

	cout << "openslide version: " << openslide_get_version() << endl;

	const char* wsi_name = "/home/hdd0/Develop/xxx/workflow/1.tif";
	openslide_t* osr = openslide_open(wsi_name);

	print_downsamples(osr);

	int64_t w, h;
	openslide_get_level0_dimensions(osr, &w, &h);
	printf("level 0 dimensions: %" PRId64 " x %" PRId64 "\n", w, h);

	test_read_region(osr);

	openslide_close(osr);
	
	return 0;
}