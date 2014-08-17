###CGI with Harp and C - Flat File and Architecture

In a previous blog post I talked about [creating a chat server] and today I'm going
to talk about the overall plan for these tutorials. It's pretty simple, we'll start
by creating a simple flat file database library to store our data. The next tutorial
will focus on using [qdecoder] to create CGI scripts to wrap the code in this tutorial 
and tie it to the web. Finally, we'll create the HTML,Basic CSS, and Javascript to 
tie our new code to our CGI and we'll suddenly have a proof of concept chat server.

<img src="/images/tech-blog/harp-apache-flatfile.png" width="400px" height="300px" style="padding-left: 25%;"/>

So without further adue, let's talk about what we need for a Chat Server from the
backend perspective: 

- A list of Users
- A way to save the chat itself

At first you might say, let's just create a flat file with a list of users! And we
could do that! And in fact it's what I did in [pchat], but since this chat server
will support multiple people talking at once, we're going to skip saving the users.
How you ask? Simply, when we submit a message to the chat server we'll submit the
user who was talking along with it. Easy enough? I think so. 

Now how do we save our chat? We can easily save it to a file and that's what we're
going to do. We're going to do the most simplistic thing we can and so long as
you're [on a unix like server] we won't worry too much about concurrency problems.

<b>The full source code for this tutorial is located [here on github]</b>

So let's get to the directory structure of the internal C code of our project! Run
the commands below to get the right structure.

    mkdir src
    mkdir src/internal
    mkdir obj 
    mkdir bin 
    mkdir headers 

Now we need to create our makefile to speed up our process, this tutorial is not an 
example of how to make Makefiles, so I'm not going to explain that much about what
this file is doing. We'll need to update it in our next tutorial to handle generating
our CGI scripts and linking against the [qdecoder] library, but for now it just 
generates our object files we need to test the innards.

_Makefile_

	#Configurations and setup
	CC = cc
	CFLAGS = -std=gnu99 -pedantic -Wall -Wextra -Werror -g -I./headers
	LINKFLAGS = $(CFLAGS) 

	INTERNAL = $(patsubst src/internal/%.c,%, $(wildcard src/internal/*.c))

	OBJECTS := $(patsubst src/%.c,obj/%.o,$(wildcard src/*.c))
	TARGETS := $(patsubst src/%.c,bin/%.cgi,$(wildcard src/*.c))
	     
	#Commands to help test and run programs:	
	valgrind = valgrind --tool=memcheck --leak-check=yes --show-reachable=yes --num-callers=20 --track-fds=yes

	all: $(TARGETS) internal
	internal: $(INTERNAL)

	$(TARGETS): $(OBJECTS) $(INTERNAL)
		${CC} ${LINKFLAGS} -o $@ $(patsubst bin/%.cgi, obj/%.o, $@ ) $(patsubst %, obj/%.o, $(INTERNAL))

	$(INTERNAL): ./headers/config.h
		${CC} ${CFLAGS} -c src/internal/$@.c -o obj/$@.o 

	clean: ./headers/config.h
		rm -f obj/*.o ${TARGETS}

	$(OBJECTS): obj/%.o : src/%.c ./headers/config.h
		${CC} ${CFLAGS} -c -o $@ $< 


We'll be placing any cgi files into the __src__ directory, and any private code into
the __internal__ directory. This will allow us to easily test our components later.

The first thing we need to do is handle configuration details. Where will we store
our data files? We'll define this in a header file:

_headers/config.h_

	#ifndef __CONFIG_H__
	#define __CONFIG_H__

	/*  Data Layer Constants */
	#define DATA_FILE "/tmp/chat.txt"
	#define BUFFER_LENGTH 32

	#endif

It's your average header file, guard includes and a few constants. The `DATA_FILE` is
where we'll store our chat history and the BUFFER_LENGTH is our base size for any string
buffer's we'll make that don't need to be dynamic.

Next we need to create some utility functions to handle talking to and writing to our
history file. We'll need to check and do the following things:

- Does the file exist?
- When was the file changed last?
- Retrieve the file for reading
- Appending new messages to the file

Not all these operation need to be exposed to user facing code, the existence of
a file does not need a public API. So we can define our header file and function 
signatures of just the ones we need like so:

_headers/internal/chatfile.h_

	#ifndef __CHATFILE_H__
	#define __CHATFILE_H__

	#include <stdlib.h>
	#include <stdio.h>
	#include <sys/stat.h>
	#include <errno.h>
	#include <string.h>
	#include <time.h>

	#include "config.h"

	/* Returns 1 if the lastCheckedTime is less than the last write to the file */
	int fileLastModifiedAfter(const char * filename, time_t lastCheckedTime);

	/* Returns NULL on err, otherwise a Read Only file descriptor for the chat file */
	FILE * getChatFile();

	/* Add a message from the user to the chat history, 1 on success 0 on err */
	int updateConversation(const char * user, const char * addendum);

	/* Initialization of chat, simply ensures the chat file exists */
	int chatInit();

	#endif

Once again, standard fair for a header file: include guard, the neccesary libraries
we'll need for the various files we'll implement, and the signatures of the methods
that will be exposed to outside sources.

We'll use **fileLastModifiedAfter** later to tell if a user needs to update their local chat
history, **getChatFile** will simply spit out the contents of our chat file and the apt-named 
**updateConversation** function will update our conversation or log an error.

The actual implement of these functions requires us to create two utility functions:

_src/internal/chatfile.c_

    #include "chatfile.h"

	static int file_exists(const char * filename){
		/* Security Concern: If you check for a file's existence and then open the 
		 * file, between the time of access checking and creation of a file someone
		 * can create a symlink or something and cause your open to fail or open 
		 * something that shouldn't be opened. That being said... I'm not concerned.
		*/
		struct stat buffer;
		return(stat (filename, &buffer) == 0);
	}

	static int create_chat_file(){	
		int chatFileExists = file_exists(DATA_FILE);
		if(chatFileExists == 0){
			FILE *fp = fopen(DATA_FILE, "w");
			if(!fp){
				chatFileExists = 0;
				fprintf(stderr,"%s %s\n", "Could not create chat file " DATA_FILE " ",  strerror(errno));
			}else{
				chatFileExists = 1;
				fclose(fp);
			}
		}
		return chatFileExists;
	}

**Note:** <small>The security concern I note in the **file_exists** function is a footnote that a
normal server shouldn't have to worry about. And if you do have to worry about it,
then that means someones on your server already and that's a bigger problem.</small>

The **file_exists** function will return 1 or 0 on if the file actually exists or not
and then **create_chat_file** function creates the chat file if it does not already
exists. Both of these functions are `static` which means they'll be local to the 
source file. 

_src/internal/chatfile.c_ (continued)

Three of the exposed methods have simple code that is easy to follow:

	int fileLastModifiedAfter(const char * filename, time_t lastCheckedTime){
		struct stat buffer;
		stat(filename, &buffer);
		return lastCheckedTime < buffer.st_mtime;
	}
	FILE * getChatFile(){
		int userFileExists = file_exists(DATA_FILE);
		if(userFileExists == 0) return NULL;

		FILE * fp = fopen(DATA_FILE, "r");
		if(!fp){
			fprintf(stderr, "Could not open chat file " DATA_FILE " for reading: %s", strerror(errno));
		}
		return fp;
	}
	int chatInit(){
		return create_chat_file();
	}

The **fileLastModifiedAfter** function uses the operating system's [stat command]
to find the `.st_mtime` field, which conains the last modification time, this compared
to the argument `lastCheckedTime` results in doing exactly what we specified in 
the header file.

**getChatFile** performs a `fopen` operation and returns the resulting pointer.
Note the use of C compile time string compilation to automatically inject the 
configured `DATA_FILE` into the error message. This is helpful for figuring out
permissions errors or any other error raised by `strerror`. Lastly, chatInit simply 
calls the `create_chat_file` function since our initialization isn't complicated.

Our last function **updateConversation** is slightly more compilicated looking,
but is really quite simple:

_src/internal/chatfile.c_ (continued)

	int updateConversation(const char * user, const char * addendum){
		FILE * fp = fopen(DATA_FILE, "a");
		
		if(!fp){
			fprintf(stderr, "Could not open chat file " DATA_FILE " for updating: %s", strerror(errno));
			return 0;
		}

		time_t t;
		struct tm * tmp;
		t = time(NULL);
		tmp = localtime(&t);
		if(tmp == NULL){
			fprintf(stderr, "Failed to determine local time\n");
			fprintf(fp, "[Unknown Time %s]: %s\n", user ,addendum);
		}else{
			char timeBuffer[30];
			bzero(timeBuffer, sizeof(timeBuffer));
			strftime(timeBuffer, sizeof(timeBuffer), "%F %I:%M", tmp);
			fprintf(fp, "[%s %s]: %s\n", timeBuffer , user ,addendum);
		}
		fflush(fp);
		fclose(fp);
		return 1;
	}

We open the history file in appending mode so that we always add new messages to
the end of our file. This not only saves us code, but results in an easier to understand
logic than trying to append new lines to the first line of the file for reading. 
We then determine the current time according to the server and use it in our message
format. Don't send me your complaints about a server spitting out the wrong time,
that's a configuration issue in apache or your computer if you run into those problems 
and is no fault of the function `localtime`.

With that, we have all the neccesary internal code to write a chat server! Surprised? 
That's ok, but you might be wondering: I don't have any visual output that any of
this stuff works, how can I be sure Ethan's not pulling a fast one on me?

Well, you can't ;) except that we're going to add a test directory and write a 
couple tests:

    mkdir test
    touch test/test-chat.c

Next we'll update our **Makefile** to compile our test for us and then use asserts
to guarantee that our code works as expected:

_Makefile_

	#Configurations and setup
	CC = cc
	CFLAGS = -std=gnu99 -pedantic -Wall -Wextra -Werror -g -I./headers
	LINKFLAGS = $(CFLAGS) 

	INTERNAL = $(patsubst src/internal/%.c,%, $(wildcard src/internal/*.c))

	OBJECTS := $(patsubst src/%.c,obj/%.o,$(wildcard src/*.c))
	TARGETS := $(patsubst src/%.c,bin/%.cgi,$(wildcard src/*.c))
	     
	#Commands to help test and run programs:	
	valgrind = valgrind --tool=memcheck --leak-check=yes --show-reachable=yes --num-callers=20 --track-fds=yes

	all: $(TARGETS) internal
	internal: $(INTERNAL)

	$(TARGETS): $(OBJECTS) $(INTERNAL)
		${CC} ${LINKFLAGS} -o $@ $(patsubst bin/%.cgi, obj/%.o, $@ ) $(patsubst %, obj/%.o, $(INTERNAL))

	$(INTERNAL): ./headers/config.h
		${CC} ${CFLAGS} -c src/internal/$@.c -o obj/$@.o 

	clean: ./headers/config.h
		rm -f obj/*.o ${TARGETS}

	$(OBJECTS): obj/%.o : src/%.c ./headers/config.h
		${CC} ${CFLAGS} -c -o $@ $< 

	test-internal:
		${CC} ${LINKFLAGS} test/test-chat.c obj/chatfile.o -o bin/test-chat.out

The addition to the file is:

    test-internal:
		${CC} ${LINKFLAGS} test/test-chat.c obj/chatfile.o -o bin/test-chat.out

This will compile our test file into a binary we can run by executing `./bin/test-chat.out`
The test itself will do the following:

- initialize the chat internals with **chatInit**
- update the chat with a message
- check the modification time to make sure it's changed
- verify that the message we chatted is there when we read the file

So without further aduei:

_test-chat.c_

	#include "chatfile.h"
	#include <assert.h>
	#include <unistd.h>

	int main(){

		/* Test init */
		int success = chatInit();
		assert(success == 1);

		/* Test adding to conversation */
		success = updateConversation("test", "I AM GROOT");
		assert(success == 1);

		sleep(1);
		/* Test modified time */
		assert(fileLastModifiedAfter(DATA_FILE, time(0)) == 0 );

		/* Test that reading converation has what was written */
		FILE * fp = getChatFile();
		assert(fp != NULL);

		char buffer[512];
		bzero(buffer, sizeof(buffer));
		fgets(buffer, sizeof(buffer), fp);
		fclose(fp);

		assert( strstr(buffer, "I AM GROOT") != NULL);
		
		return 0;
	}

This test simply calls each of our methods and `assert`s that they work as we
expect them to. Assert's are a great way to guarantee a contract with your code.
They're good for some development processes (not all) and can be used to make
sure your code is error free. To test your own implementation use the following 
commands:

    make test-internal 
    ./bin/test-chat.out

If you don't get any errors, then you're good to go! You can also check out the
`DATA_DIR` file and see that things are being written to it. 

This wraps up the tutorial, stay tuned for the next installment for how to expose
these internal functions to the web using CGI and [qdecoder]! Believe it or not,
we've done the hard part of designing our application and writing the fundamental 
peaces of our core code. We've tested them to ensure they're correct, and we've
made a simple API for our other code to talk to when we implement it. In the next
tutorial not only will we add qdecoder and learn how to write basic CGI, but we'll
create an API that will expose our resources to the web.

See you next time!




[creating a chat server]:http://www.ethanjoachimeldridge.info/tech-blog/privateTalk
[Harp]:http://harpjs.com
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[pchat]:https://github.com/EJEHardenberg/pChat
[on a unix like server]:http://stackoverflow.com/a/12943431/1808164
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[stat command]:http://linux.die.net/man/2/stat