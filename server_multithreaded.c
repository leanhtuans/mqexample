#include <errno.h>
#include <pthread.h>
#include <sys/syscall.h>

#include "common.h"

pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mutx = PTHREAD_MUTEX_INITIALIZER;
char buffer[MAX_SIZE + 1];
int must_stop = 0;
	
void *data_receiver(void *arg)
{
	printf("data_receiver thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
    mqd_t mq;
    struct mq_attr attr;

    /* initialize the queue attributes */
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = MAX_SIZE;
    attr.mq_curmsgs = 0;

    /* create the message queue */
    mq = mq_open(QUEUE_NAME, O_CREAT | O_RDONLY, 0644, &attr);
    CHECK((mqd_t)-1 != mq);

    do {
        ssize_t bytes_read;

        /* receive the message */
		pthread_mutex_lock(&mutx);
		printf("data_receiver thread: waiting data...\n");
		bytes_read = mq_receive(mq, buffer, MAX_SIZE, NULL);
		CHECK(bytes_read >= 0);		
		buffer[bytes_read] = '\0';		
		printf("data_receiver thread: received data: %s.\n", buffer);
		pthread_mutex_unlock(&mutx);
		pthread_cond_signal(&cv);
    } while (!must_stop);

    /* cleanup */
    CHECK((mqd_t)-1 != mq_close(mq));
    CHECK((mqd_t)-1 != mq_unlink(QUEUE_NAME));

	printf("data_receiver thread terminated!\n");
    return NULL;
}

void *data_proccessing(void* arg)
{
	printf("data_proccessing thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
    do
	{
		pthread_mutex_lock(&mutx);
		printf("data_proccessing thread: waiting data...\n");
		while (!buffer[0])
			pthread_cond_wait(&cv, &mutx);
		printf("data_proccessing thread: received data: %s.\n", buffer);
		if (! strncmp(buffer, MSG_STOP, strlen(MSG_STOP)))
		{
			must_stop = 1;
		}
		else
		{
			printf("Received: %s\n", buffer);
		}
		buffer[0] = '\0';
		pthread_mutex_unlock(&mutx);
    }while(!must_stop);
	
	printf("data_proccessing thread terminated!\n");
    return NULL;
}

int main(int argc, char **argv)
{
	pthread_t tiddata_receiver;
	pthread_t tiddata_proccessing;
	printf("Main thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
	
	pthread_create(&tiddata_proccessing, NULL, data_proccessing, NULL);
	pthread_create(&tiddata_receiver, NULL, data_receiver, NULL);
	
	pthread_join(tiddata_receiver, NULL);
	pthread_join(tiddata_proccessing, NULL);
	
	return 0;
}





















