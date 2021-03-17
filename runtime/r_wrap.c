#include "r_split.h"
#include <unistd.h>
#include <sys/wait.h>

#define READ_END 0
#define WRITE_END 1

void processCmd(char *args[])
{
    size_t bufLen = BUFLEN, outBufLen = BUFLEN; //buffer length, would be resized as needed
    int64_t id;
    size_t blockSize;
    char *buffer = malloc(bufLen + 1);
    char *readBuffer = malloc(bufLen + 1);
    char *cmdOutput = malloc(outBufLen+1);
    //select
    fd_set readFds;
    fd_set writeFds;
    int maxFd;

    readHeader(stdin, &id, &blockSize);
    while (!feof(stdin))
    {
        int fdIn[2];
        int fdOut[2];
        if (pipe(fdIn) < 0)
        {
            perror("pipe failed");
            exit(1);
        }

        if (pipe(fdOut) < 0)
        {
            perror("pipe failed");
            exit(1);
        }

        int pid = fork();
        if (pid == 0)
        {
            dup2(fdOut[WRITE_END], STDOUT_FILENO);
            dup2(fdIn[READ_END], STDIN_FILENO);

            close(fdOut[READ_END]);
            close(fdOut[WRITE_END]);
            close(fdIn[READ_END]);
            close(fdIn[WRITE_END]);
            // free(buffer); copy-on-write fork optimize this better(freeing is more harm than good here)
            execvp(args[0], args);
            //shouldn't get here
            perror("Exec failed");
            exit(1);
        }
        else
        {
            close(fdIn[READ_END]);
            close(fdOut[WRITE_END]);

            int inputFd = fdOut[READ_END];
            int outputFd = fdIn[WRITE_END];

            FILE *execOutFile = fdopen(inputFd, "rb");
            FILE *execInFile = fdopen(outputFd, "wb");
            fcntl(inputFd, F_SETFL, O_NONBLOCK);

            size_t len = 0, currLen = 0;

            //select prep
            maxFd = MAX(inputFd, outputFd);

            //Read batch
            size_t tot_read = 0, readSize = 0;
            while (tot_read < blockSize)
            {
                readSize = MIN(bufLen, blockSize - tot_read);
                // fprintf(stderr, "reading stdin\n");
                if (fread(buffer, 1, readSize, stdin) != readSize)
                {
                    fprintf(stderr, "r_wrap: There is a problem with reading the block\n");
                    exit(1);
                }
<<<<<<< HEAD

=======
<<<<<<< HEAD
                //Try reading from forked processs, nonblocking
                while ((len = fread(readBuffer, 1, bufLen, execOutFile)) > 0) {
                    if ((currLen + len) > outBufLen) {
                        outBufLen = currLen + len + CHUNKSIZE;
                        cmdOutput = realloc(cmdOutput, outBufLen + 1);
                    }
                    memcpy(cmdOutput + currLen, readBuffer, len);
                    currLen += len;
                    // fprintf(stderr, "read %ld bytes\n", len);
                }

=======
                FD_ZERO(&readFds); // Clear FD set for select
>>>>>>> refs/rewritten/round-split-4
                FD_ZERO(&writeFds); // Clear FD set for select
                while (!FD_ISSET(outputFd, &writeFds))
                {
                    // fprintf(stderr, "looping select\n");
                    FD_ZERO(&readFds);  // Clear FD set for select
                    FD_ZERO(&writeFds); // Clear FD set for select
                    FD_SET(inputFd, &readFds);
                    FD_SET(outputFd, &writeFds);

                    // TODO: Should I handle some error here?
                    select(maxFd + 1, &readFds, &writeFds, NULL, NULL);
                    if (FD_ISSET(inputFd, &readFds))
                    {
                        //Try reading from forked processs, nonblocking
                        len = fread(readBuffer, 1, bufLen, execOutFile);
                        if ((currLen + len) > outBufLen)
                        {
                            outBufLen = currLen + len + CHUNKSIZE;
                            cmdOutput = realloc(cmdOutput, outBufLen + 1);
                        }
                        memcpy(cmdOutput + currLen, readBuffer, len);
                        currLen += len;
                    }
                }
                // fprintf(stderr, "writing %ld bytes\n", readSize);
>>>>>>> refs/rewritten/round-split-3
                //Write to forked process
                safeWriteWithFlush(buffer, 1, readSize, execInFile);

                tot_read += readSize;
            }
            fclose(execInFile);
            // fprintf(stderr, "finished one fork\n");
            assert(tot_read == blockSize);

            //read output of forked process (do I need to wait or is read blocking enough?)
            //Use nonblock to make sure you read until the process exits
            fcntl(inputFd, F_SETFL, ~O_NONBLOCK);
            while ((len = fread(buffer, 1, bufLen, execOutFile)) > 0)
            {
                if ((currLen + len) > outBufLen)
                {
                    outBufLen = currLen + len + CHUNKSIZE;
                    cmdOutput = realloc(cmdOutput, outBufLen + 1);
                }
                memcpy(cmdOutput + currLen, buffer, len);
                currLen += len;
            }
            fclose(execOutFile);

            //write block to stdout
            writeHeader(stdout, id, currLen);
            safeWriteWithFlush(cmdOutput, 1, currLen, stdout);

            //update header (ordered at the end so !feof works) and cleanup
            readHeader(stdin, &id, &blockSize);
        }
        kill(pid, SIGKILL);
    }
    free(buffer);
    free(readBuffer);
    free(cmdOutput);
}

int main(int argc, char *argv[])
{
    //arg1: command
    //args 2.. : arguments for command
    //input is from stdin, out to stdout
    char **args = NULL;
    if (argc < 2)
    {
        /* default behavior is to echo all the filenames */
        fprintf(stderr, "missing input!\n");
        exit(1);
    }

    //process arguments
    args = malloc(sizeof(char *) * (argc));
    for (int i = 1; i < argc; i++)
    {
        args[i - 1] = malloc(strlen(argv[i]) + 1);
        strcpy(args[i - 1], argv[i]);
    }
    args[argc - 1] = '\0';
    processCmd(args);
}
