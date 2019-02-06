// gcc posix-shm-server.c -o posix-shm-server -lrt

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/mman.h>



int main (int argc, char *argv[]) {
	const char * shm_name  = "/AOS";
    const int SIZE = 4096;
    const char * message[] = {"This ", "is ", "custom ", "code", "\n"};

    int i, shm_fd;
    void * ptr;
    shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
    if (shm_fd == 1) {
		printf("Shared memory segment failed\n");
		exit(1);
	}

    ftruncate(shm_fd, sizeof(message));
    ptr = mmap(0, SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (ptr == MAP_FAILED) {
        printf("Map failed\n");
        return 1;
    }

	/* Write into the memory segment */
    for (i = 0; i < strlen(*message); ++i) {
        sprintf(ptr, "%s", message[i]);
        ptr += strlen(message[i]);
    }
    munmap(ptr, SIZE);

    return 0;
}