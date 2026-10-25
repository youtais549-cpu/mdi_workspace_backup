#include <mpi.h>
#include <stdio.h>
int main(int argc, char** argv) {
    char err_buffer[MPI_MAX_ERROR_STRING];
    int resultlen;
    MPI_Error_string(9035, err_buffer, &resultlen);
    printf("MPI Error 9035: %s\n", err_buffer);
    return 0;
}
