// gcc posix-shm-client.c -o posix-shm-client -lrt

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/mman.h>


int main (int argc, char *argv[]) {
	const char * shm_name  = "/AOS";
    const int SIZE = 4096;

    int i, shm_fd;
    void * ptr;
    
    shm_fd = shm_open(shm_name, O_RDONLY, 0666);
    if (shm_fd == 1) {
		printf("Shared memory segment failed\n");
		exit(1);
	}

	ptr = mmap(0, SIZE, PROT_READ, MAP_SHARED, shm_fd, 0);
    if (ptr == MAP_FAILED) {
        printf("Map failed\n");
        return 1;
    }

	printf("%s", (char *) ptr);
	if (shm_unlink(shm_name) == 1) {
		printf("Error removing %s\n", shm_name);
		exit(1);
	}
	   
	return 0;
}