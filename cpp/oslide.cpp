// g++ -o oslide oslide.cpp -I/usr/local/include -I/usr/local/include/openslide -std=c++11

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <iostream>
#include <math.h>
#include <stdint.h>
#include <inttypes.h>
#include <assert.h>
#include <sys/time.h>

#include "openslide.h"

using namespace std;


static void print_downsamples(openslide_t *osr) {
	for (int32_t level = 0; level < openslide_get_level_count(osr); level++) {
		printf("level %d: downsample: %g\n",
			   level,
			   openslide_get_level_downsample(osr, level));
	}
}



int main(int argc, char** argv) {

	cout << 123 << endl;

	print_downsamples(NULL);

	return 0;
}