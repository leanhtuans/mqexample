#include "common.h"


int main(int argc, char **argv)
{
    mqd_t mq;
	
	BAO_msg_t msg;

    /* open the mail queue */
    mq = mq_open(QUEUE_NAME, O_WRONLY);
    CHECK((mqd_t)-1 != mq);


    printf("Send to server (enter \"exit\" to stop it):\n");

    while (1)
	{
        printf("> ");
        fflush(stdout);
		
        memset(msg.content, 0, MAX_SIZE);
        fgets(msg.content, MAX_SIZE, stdin);
		msg.content[strlen(msg.content)-1] = '\0';

		if (! strncmp(msg.content, MSG_STOP, strlen(MSG_STOP)))
		{
			msg.message = BAO_STOP_REQ;
			/* send the message */
			CHECK(0 <= mq_send(mq, (char*)&msg, MAX_SIZE, 0));
			break;
		}
		
        /* send the message */
        CHECK(0 <= mq_send(mq, (char*)&msg, MAX_SIZE, 0));
    }

    /* cleanup */
    CHECK((mqd_t)-1 != mq_close(mq));

    return 0;
}
