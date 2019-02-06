echo "compiling"
gcc posix-shm-server.c -o posix-shm-server -lrt
gcc posix-shm-client.c -o posix-shm-client -lrt

echo "executing"
./posix-shm-server
./posix-shm-client