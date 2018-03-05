#include <errno.h>
#include <pthread.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>

#include "common.h"

pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mutx = PTHREAD_MUTEX_INITIALIZER;
	
void *data_receiver(void *arg)
{
	printf("data_receiver thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
    mqd_t mq;
    struct mq_attr attr;	
	BAO_msg_t msg;
	
    ssize_t bytes_read;
	
	pthread_t tiddata_proccessing;

    /* initialize the queue attributes */
    attr.mq_flags = 0;
    attr.mq_maxmsg = 3;
    attr.mq_msgsize = sizeof(msg);
    attr.mq_curmsgs = 0;

    /* create the message queue */	
    mq = mq_open(QUEUE_NAME, O_CREAT | O_RDONLY, 0644, &attr);
    CHECK((mqd_t)-1 != mq);

    while (1)
	{

        /* receive the message */
//		printf("data_receiver thread: waiting data...\n");
		pthread_mutex_lock(&mutx);
		bytes_read = mq_receive(mq, (char*)&msg, sizeof(msg), NULL);
		CHECK(bytes_read >= 0);
		printf("data_receiver thread: received data: %s.\n", msg.content);
		pthread_mutex_unlock(&mutx);
		if (BAO_STOP_REQ == msg.message)
		{
			break;			
		}
		else
		{
			pthread_create(&tiddata_proccessing, NULL, data_proccessing, (void*)&msg);
			usleep(1000);
		}
		//pthread_cond_signal(&cv);
    }

    /* cleanup */
    CHECK((mqd_t)-1 != mq_close(mq));
    CHECK((mqd_t)-1 != mq_unlink(QUEUE_NAME));

	printf("data_receiver thread terminated!\n");
    return NULL;
}

void *data_proccessing(void* msg)
{	
	printf("data_proccessing thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
	
	BAO_msg_t rec_msg;
	pthread_mutex_lock(&mutx);
	memcpy(&rec_msg, msg, sizeof(rec_msg));
	pthread_mutex_unlock(&mutx);
	
    //do
	//{
//		printf("data_proccessing thread: waiting data...\n");
		//while (!buffer[0])
		//	pthread_cond_wait(&cv, &mutx);
//		printf("data_proccessing thread: received data: %s.\n", buffer);
		//if (! strncmp(buffer, MSG_STOP, strlen(MSG_STOP)))
		//{
		//	must_stop = 1;
		//}
		//else
		//{
			printf("Received: %s\n", rec_msg.content);
		//}
		//buffer[0] = '\0';
    //}while(!must_stop);
	
	printf("data_proccessing thread terminated!\n");
    return NULL;
}

int main(int argc, char **argv)
{
	//pthread_t tiddata_proccessing;
	pthread_t tiddata_receiver;
	printf("Main thread, PID %d TID %d\n", getpid(), (pid_t)syscall(SYS_gettid));
	
	//pthread_create(&tiddata_proccessing, NULL, data_proccessing, NULL);
	//sleep(1);
	pthread_create(&tiddata_receiver, NULL, data_receiver, NULL);
	
	pthread_join(tiddata_receiver, NULL);
//	pthread_join(tiddata_proccessing, NULL);
	
	return 0;
}





















