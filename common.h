#ifndef COMMON_H_
#define COMMON_H_

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <mqueue.h>

#define QUEUE_NAME  "/test_queue"
#define MAX_SIZE    1024
#define MSG_STOP    "exit"

#define CHECK(x) \
    do { \
        if (!(x)) { \
            fprintf(stderr, "%s:%d: ", __func__, __LINE__); \
            perror(#x); \
            exit(-1); \
        } \
    } while (0) \

typedef enum {
	BAO_START_REQ,
	BAO_STOP_REQ,
	BAO_QUESTION_REQ,
	BAO_ANSWER_REQ
} BAO_IPC_MSG;
	
typedef struct _bao_msg_t {
	BAO_IPC_MSG message;
	char content[MAX_SIZE + 1];
} BAO_msg_t;
	
void *data_proccessing(void* msg);
void *data_receiver(void *arg);

#endif /* #ifndef COMMON_H_ */
