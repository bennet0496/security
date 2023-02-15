#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include<signal.h>
#include <telebot.h>

#define SIZE_OF_ARRAY(array) (sizeof(array) / sizeof(array[0]))
#define BLOCK_SIZE 255
#define TOKEN_LENGTH 1024

bool INTERRUPTED = false;

void handle_sigint(int sig) {
    printf("Caught signal %d\n", sig);
    if (sig == SIGINT) {
        INTERRUPTED = true;
    }
}

void poll_updates(telebot_handler_t handle) {
    int index, count, offset = -1;
    telebot_error_e ret;
    telebot_message_t message;
    telebot_update_type_e update_types[] = {TELEBOT_UPDATE_TYPE_MESSAGE};

    signal(SIGINT, handle_sigint);

    while (!INTERRUPTED) {
        telebot_update_t *updates;
        ret = telebot_get_updates(handle, offset, 20, 0, update_types, 0, &updates, &count);
        if (ret != TELEBOT_ERROR_NONE) {
            continue;
        }
        printf("Number of updates: %d\n", count);
        for (index = 0; index < count; index++) {
            message = updates[index].message;
            if (message.text) {
                printf("%s (ID: %d, @%s): %s \n", message.from->first_name, message.from->id, message.from->username, message.text);
                
                char str[4096];
                
                snprintf(str, SIZE_OF_ARRAY(str), "Hello %s, your ID is %d", message.from->first_name, message.from->id);
            
                ret = telebot_send_message(handle, message.chat->id, str, "HTML", false, false, updates[index].message.message_id, "");
                
                if (ret != TELEBOT_ERROR_NONE)
                {
                    printf("Failed to send message: %d \n", ret);
                }
            }
            offset = updates[index].update_id + 1;
        }
        telebot_put_updates(updates, count);

        sleep(1);
    }
}

int main(int argc, const char ** argv, const char ** envp) {
    FILE* fp;
    char* token;
    telebot_handler_t handle;
    telebot_user_t me;
    long long chat_id;
    telebot_error_e ret;
    char *str;
    char rstr[BLOCK_SIZE];
    unsigned long long int ctr = BLOCK_SIZE;
    bool start_polling = false;

    if (argc > 0) {
        //detect chats -> id retrival
        if(strcmp(argv[1], "-d") == 0) {
            start_polling = true;
        } else {
            chat_id = atoll(argv[1]);
            if (chat_id == 0ll){
                printf("Malfromed destination chat\n");
                return EXIT_FAILURE;
            }
        }
    }

    token = getenv("TELEGRAM_TOKEN");

    fp = fopen(".token", "r");
    if (fp == NULL && token == NULL) {
        printf("Failed to open .token file or read TELEGRAM_TOKEN variable\n");
        return EXIT_FAILURE;
    }

    //printf("Token: %s\n", token);

    if (token == NULL) {
        token = calloc(TOKEN_LENGTH, sizeof(char));
        if (fscanf(fp, "%s", token) == 0) {
            printf("Failed to read token\n");
            fclose(fp);
            return EXIT_FAILURE;
        }
    }

    //printf("Token: %s\n", token);
    //fclose(fp);

    if (telebot_create(&handle, token) != TELEBOT_ERROR_NONE) {
        printf("Telebot create failed\n");
        return EXIT_FAILURE;
    }

    if (telebot_get_me(handle, &me) != TELEBOT_ERROR_NONE) {
        printf("Failed to get bot information. Do we exist and are online?\n");
        telebot_destroy(handle);
        return EXIT_FAILURE;
    }

    //printf("ID: %d\n", me.id);
    //printf("First Name: %s\n", me.first_name);
    //printf("User Name: %s\n", me.username);

    telebot_put_me(&me);

    if (start_polling) {
        poll_updates(handle);
    } else {
        if (chat_id == 0ll) {
            printf("To: ");
            scanf("%lld", &chat_id);
        }

        str = (char*)calloc(BLOCK_SIZE, sizeof(char));

        while(read(STDIN_FILENO, &rstr[0], BLOCK_SIZE) != 0) {
            ctr += BLOCK_SIZE;
            str = (char*)realloc(str, ctr);
            strcat(str, rstr);
        }
        
        ret = telebot_send_message(handle, chat_id, str, "HTML", false, false, -1, "");
    }

    telebot_destroy(handle);

    return EXIT_SUCCESS;
}