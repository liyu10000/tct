// g++ -o mprocess mprocess.cpp

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

/* Write COUNT copies of MESSAGE to STREAM, pausing for a second
   between each.  */
void writer(const char * message, int count, FILE * stream) {
  for(; count > 0; count) {
    fprintf(stream, "%s\n", message);
    fflush(stream);
    sleep(1);
  }
}

void reader(FILE * stream) {
  char buffer[1024];
/* Read until we hit the end of the stream.  fgets reads until
     either a newline or the end­of­file.  */
  while(!feof(stream) && !ferror(stream)
&& fgets(buffer, sizeof(buffer), stream) != NULL) 
    fputs(buffer, stdout);
} 


int main () {
  FILE * stream;
  /* Create pipe place the two ends pipe file descriptors in fds */
  int fds[2];
  pipe(fds);
  pid_t pid = fork();
  if(pid == (pid_t) 0) { /* Child process (consumer) */
    close(fds[1]);          /* Close the copy of the fds write end */
    stream = fdopen(fds[0], "r");
    reader(stream);
    close(fds[0]);
  }
  else {                   /* Parent process (producer)  */
    close(fds[0]);         /* Close the copy of the fds read end */
    stream = fdopen(fds[1], "w");
    writer("Hello, world.", 3, stream);
    close(fds[1]);
  }
  return 0;
}