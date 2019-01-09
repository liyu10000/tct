#include <stdio.h>
#include <stdlib.h>
#include <iostream>

using namespace std;


void param_passing(const char * arr[], int l) {
	for (int i = 0; i < l; i++) {
		cout << arr[i] << endl;
	}
}


int main(int argc, char** argv) {
	int x = 5, *aptr;
	aptr = &x;
	cout << *aptr << endl;

	const char *a = "123", *b = "123";

	if (a == b) {
		cout << "the same" << endl;
	}

	const char* arr[] = {"123", "244", "434"};
	param_passing(arr, 3);

	
	return 0;
}