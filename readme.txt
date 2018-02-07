gcc -o client client.c -lrt
gcc -o server server.c -lrt
gcc -o server_multithreaded server_multithreaded.c -lrt -pthread -g