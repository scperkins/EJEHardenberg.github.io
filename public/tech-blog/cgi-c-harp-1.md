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

__Makefile__

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




[creating a chat server]:http://www.ethanjoachimeldridge.info/tech-blog/privateTalk
[Harp]:http://harpjs.com
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[pchat]:https://github.com/EJEHardenberg/pChat
[on a unix like server]:http://stackoverflow.com/a/12943431/1808164
[here on github]:https://github.com/EJEHardenberg/chat-tutorial