###CGI with Harp and C - QDecoder and Apache

Welcome to round 2 of "Let's create a chat server!", if you missed the [previous post] 
then you'll want to read that to get up to speed. If you just want to grab the
source code from that tutorial you can find it [here on github].

In this tutorial we're going to take the work we did last time (what I refer to as
internals) and use the [qdecoder] library to make it web facing. I'll show you the
neccesary apache configuration for using CGI and give a brief explanation into
some of the basics of CGI. So let's get started:

####Install Apache and qdecoder

First off, you'll need apache (or some other webserver)  setup. If you're running
linux this is normally as easy as:

    sudo apt-get install apache2

If you're on windows you can download a bundle like [xampp] or [wamp] and install the
binary by following the instructions on their pages. Most mac's come preinstalled
with some type of webserver, but I don't own a mac so you're on your own.

To install the qdecoder library you'll need to follow [their instructions] and 
download the source and build the static library. It's not difficult to do, for me
the steps were something like this:

1. Download the latest qdecoder package [from here]
2. run `./configure` to setup the library for you system
3. compile the library with `make`
4. install the library with `make install`

Which are literally the steps out of the **INSTALL.md** file in the repository. 
I've only installed qdecoder on linux, so if you're trying to do this on windows
or mac you'll want to get your [google fu] on to figure it out. I believe, (don't
qoute me on this) that the mac install should be the exact same as what I've said
above since it's a unix based operating system.

Once you've installed the library, try building some of the [examples] to make
sure everything is working. Once you've got that come back here. For the purpose
of my tutorial I'll assume you built it from source and installed it into a folder
called **lib** within your working directory.

####Using qdecoder

The library has some great [examples] and if you haven't looked at them, seriously
do so. If you've ever done web programming before, chances are some of this stuff
will look and feel familiar to you. And even if it doesn't you'll probably be able
to take a good guess. Let's take an overview of the functions we're going to use:

    FCGI_Accept

If you've configured qdecoder with fast CGI, then you'll be using this function
to keep your script running (as oppose to turning on and off for each request).
The library provides a simple define to check for the configuration, so you'll
see this in a few places as a fallback in case the library doesn't support it:

    #ifdef ENABLE_FASTCGI
        while(FCGI_Accept() >= 0) {
    #endif

    //code ...

    #ifdef ENABLE_FASTCGI
        }
    #endif

**Note**: <small>If you're unfamiliar with the C Preprocessor, all you need to know 
is that the code between the `ifdef` and `endif` will only be used if the `ENABLE_FASTCGI`
constant is defined. If it's not, just think of the code as being commented out.</small>

    qcgireq_parse

The `qcgireq_parse` function handles the hard part about taking the environmental
variable sent to apache and parsing them into a useful way. If you've used PHP before
you can think of this as what your server does as it puts variables into the super
globals `$_GET`,`$_POST`, `$_COOKIE`, and etc. qDecoder parses the servers in 
COOKIE, POST, then GET order. If you want to change that ordering you can find out
how in the [documentation]. The `qcgireq_parse` function takes two parameters:
a `qentry_t` pointer and a flag on parsing order. If you pass `NULL` as the first 
parameter you'll be given back a `qentry_t` variable with all the variables stored
in it, this is what we'll be doing. So far, the only time I've seen a non-NULL value
passed is for getting the parameters in a specific order.

    qcgires_setcontenttype

This function allows you to set the HTML header for the content type. qDecoder does
**not** allow you to set any headers you want. Rather, it provides methods to set
the content type and to send redirect headers. Most applications really don't need
much more than this so it's a pragmatic choice and keeps the library code less
complex and the API simple. We'll be using 2 content types in our scripts: `text/plain`
and `application/JSON`. 

	qentry_t->getstr, qentry->free

These two functions are two of the ways we can interact with a request object, when
`qcgireq_parse` returns a struct of type `qentry_t` you can use `->getstr` to retrieve
a variable from the parsed values, and use `->free` to release your request object.

Here's some equalvalent code between PHP and qDecoder for some clarification:

_PHP_

    $myvar = $_GET['theVarInTheUrl'];
    $mypvar = $_POST['theVarInThePostedData'];

and in _C_

    qentry_t *req = qcgireq_parse(NULL, 0);
    char * myvar = req->getstr(req, "theVarInTheUrl", true);
    char * mypvar = req->getstr(req, "theVarInThePostedData", false);
    req->free(req);

Not much difference besides having to parse the request. Also, you'll notice I 
used `true` in one call to `->getstr` and not in the other. The third parameter
to the `->getstr` method is whether or not the caller is responsible for freeing
the string returned to them or not. If you're in a **single** thread environment
then you'll safe to use false and you won't need to worry about `free`-ing the strings
you from the request (so long as you free the request itself), but if you're working
in a multithreaded application you'll want to use `true` and free them when you can.

Another difference to note is that we do not have seperate calls for `GET` or `POST`
but in this case, because we've passed `0` as the second parameter to `qcgireq_parse` 
we get ALL values sent to us. If you wanted to make a couple of global variables for 
yourself you could do this:

    qentry_t *_POST = qcgireq_parse(NULL, Q_CGI_POST);
    qentry_t *_GET = qcgireq_parse(NULL, Q_CGI_GET);

and then use each one accordingly.

The last thing I want to touch on is an error message you might see in your logs 
when attempting to debug your scripts: 

    Premature end of script headers

This means that you tried to output content before you set the content type of the 
request. If you're looking at your code saying "no way, I set it right there!",
then there's a good chance you're dealing with some undefined behavior in your 
scripts, a variable isn't initialized properly, you've written somewhere you 
shouldn't or you've read somewhere you definitely shouldn't have. All of these
things will cause that error. And if you're lucky, you'll get a memory dump in 
your error log for you to decipher. <b>This is why we tested our internal code
in the last tutorial</b>, and it's always a good idea to do so. Also, use [valgrind] 
to test everything you do! (more on that in a bit!)

####Your first qdecoder script 

We're going to make a heartbeat script. This is a standard API trick, it's simple
to make, and when you want to know if your server is still functioning it's a good
way to check. Some heartbears can be complicated, but our's is going to be super
simple. We'll simply spit out the time and make sure the chat is initialized. 
Check it out:

_src/heartbeat.c_

    #include "config.h"
    #include "chatfile.h"
    #include "load_qdecoder.h"

    int main(void){
    #ifdef ENABLE_FASTCGI
        while(FCGI_Accept() >= 0) {
    #endif
        qentry_t *req = qcgireq_parse(NULL, Q_CGI_GET);
        qcgires_setcontenttype(req, "application/JSON");

        int initialized = chatInit();

        printf("{ \"heartbeat\" : %ld, \"initialized\" : %s }", time(0), initialized ? "true" : "false");

        // De-allocate memories
        req->free(req);
    #ifdef ENABLE_FASTCGI
        }
    #endif
        return 0;
    }


In order to compile this program we'll need to load the qdecoder library, which
means updating our **Makefile** a little bit. Add the following to the top of
your Makefile underneath the `LINKFLAGS`

    LIBS = lib/wolkykim-qdecoder-63888fc/src/libqdecoder.a

**Note**:<small>If you've installed qdecoder somewhere other than lib, you'll need
to reflect that in the definition above. I downloaded the source, untar-ed it, and
placed it into a **lib** folder, you might have done something else.</small>

And then change the line that looks like this:

    ${CC} ${LINKFLAGS} -o $@ $(patsubst bin/%.cgi, obj/%.o, $@ ) $(patsubst %, obj/%.o, $(INTERNAL)) 

to this:

    ${CC} ${LINKFLAGS} -o $@ $(patsubst bin/%.cgi, obj/%.o, $@ ) $(patsubst %, obj/%.o, $(INTERNAL)) ${LIBS}

Lastly, we need to define the header file **load_qdecoder.h** which we've mentioned
at the top of the heartbeat script. Here's the header:

_load_qdecoder.h_

    #ifndef __LOAD_QDECODER_H__
    #define __LOAD_QDECODER_H__

    #ifdef ENABLE_FASTCGI
        #include "fcgi_stdio.h"
    #else
        #include <stdio.h>
    #endif
    #include "qdecoder.h"

    #endif

The only thing special about this include is that we are once again checking if
we're using fast CGI or not, and if we are, then we need to include the appropriate
standard I/O library.

Now run `make` and if you've got everything set up correctly, you'll be awarded with an
output like this:

    make
    cc -std=gnu99 -pedantic -Wall -Wextra -Werror -g -I./headers -c src/internal/chatfile.c -o obj/chatfile.o 
    cc -std=gnu99 -pedantic -Wall -Wextra -Werror -g -I./headers  -o bin/heartbeat.cgi  obj/heartbeat.o  obj/chatfile.o lib/wolkykim-qdecoder-63888fc/src/libqdecoder.a

If you run your compiled file you should receive a heartbeat response:

    ./bin/heartbeat.cgi
    Content-Type: application/JSON

    { "heartbeat" : 1408487034, "initialized" : true }

and now that we're alive, we can get to the fun stuff! Wiring your internal functions
from the previous tutorial into CGI scripts!

#### Polling, Reading, and Writing with CGI and Internals

We now have enough knowledge to implement every function which our chat server
needs:

- Polling: Check if the user needs to refresh their copy of the conversation
- Writing: Send a message to the chat server
- Reading: Retrieve the current chat history


#### _Polling_

Let's define our contract: The user will send us an epoch timestamp of when they last
retrieved the history for the chat. If this timestamp is less than the last 
modification time of our history file, we know that the history has been updated. 
Sounds like the perfect opportunity to make use of our function `fileLastModifiedAfter`!

If you recall, the function has a signature like so:

    int fileLastModifiedAfter(const char * filename, time_t lastCheckedTime);

we know the filename (It's a constant), and now we just need a `time_t` value. Well,
we know that `time_t` is defined to be `int`, `long int`, `float`, or whatever your 
system/compiler feels like, so we need to be sure we store the result into something
big enough. Then we'll convert it to the proper type and use it. This will also
give us the chance to perform some data validation (it is _user_ input after all). 

For ease of use later on, let's say we'll send back a JSON object that looks like
this:

    {"updated": true /* or false */}

And with that, our contract is defined and signed with the outside word. Easily
enough, we can translate out above specification into the following CGI script:

_poll.c_

    #include "config.h"
    #include "chatfile.h"
    #include "load_qdecoder.h"

    static void printUpdated(int updated){
        printf("{\"updated\": %s}", updated ? "true" : "false");
    }

    int main(void){
        chatInit();
    #ifdef ENABLE_FASTCGI
        while(FCGI_Accept() >= 0) {
    #endif
        qentry_t *req = qcgireq_parse(NULL, Q_CGI_GET);
        char * sentTime = NULL; 
        long long intermediateTime = 0L;
        time_t parsedTime = 0;
        qcgires_setcontenttype(req, "application/json");

        sentTime = req->getstr(req, "date", true);
        if(sentTime == NULL){
            /* They did not send us a proper request. */
            printUpdated(0);
            goto end;
        }

        int scanned = sscanf(sentTime, "%lld", &intermediateTime);
        if(scanned != 1){
            /* Incorrect format likely since we couldn't parse it out */
            printUpdated(0);
            free(sentTime);
            goto end;
        }

        parsedTime = (time_t)intermediateTime;

        int updated = fileLastModifiedAfter(DATA_FILE, parsedTime);
        printUpdated(updated);
        
        free(sentTime);
        // De-allocate memories
        end:
        req->free(req);
    #ifdef ENABLE_FASTCGI
        }
    #endif
        return 0;
    }

This source code is a bit longer than before, but simple. First, we ensure that
the chat server is initialized with `chatInit`. I do this before the Fast CGI accept
becuase we know that our initialization is just creating a file, which only really
needs to be done once. Next, we parse our request for `GET` variables using the `Q_CGI_GET` 
flag to the `qcgireq_parse` function. We then ensure that the expected URL parameter
of `date` was sent to us, convert it to a `time_t` type, and finally use our
internal function `fileLastModifiedAfter` to check whether or not the file's been updated
since the `parsedTime`.

You might be wondering? How do I test this script since it takes a URL parameter. 
We don't have any URL's after all! It's simple my friends! CGI is really nothing
more than passing information along in Environmental variables, because of this
it's easy to specify a variable on the command line and "pass" it to the script.
For example here are some tests of our poll script:

    make
    QUERY_STRING="date=no" ./bin/poll.cgi 
        Content-Type: application/json

        {"updated": false}

    QUERY_STRING="date2=100000000000" ./bin/poll.cgi 
        Content-Type: application/json

        {"updated": false}

    QUERY_STRING="date=1" ./bin/poll.cgi 
        Content-Type: application/json
            
        {"updated": true}

You can see that it works correctly, a non identegral `date` or no `date` parameter 
at all means we get `false`, and if we send in an actual time we'll get `true`.
Running these scripts from the command line and verifying their correctness is
something you should always try to do, and we can update out **Makefile** to perform
these tests for us:

_Makefile_

    #...previous code above...
    test-poll:
        QUERY_STRING="date=no" ${valgrind} ./bin/poll.cgi
        QUERY_STRING="date=1" ${valgrind} ./bin/poll.cgi
        QUERY_STRING="date=100000000000" ${valgrind} ./bin/poll.cgi
        QUERY_STRING="" ${valgrind} ./bin/poll.cgi

And then running `make test-poll` will valgrind each of the scenarios we are trying 
to test our poll script for. I **highly** recommend using [valgrind] when testing
for undefined behavior as it is _immensely_ helpful in pretty much all circumstances.
With this code we can now poll our chat server's file! Now we need to write to it:

#### _Writing_

In order for a chat server to work, people need to be able to chat! So we'll need
to define a protocol for user A to talk to user B by sending a message of some kind.
Easy enough, let's say that with each submission the chatter sends their username
and their message to the server within a `POST` request. We'll use the standard
web format of `parameter=value&param2=value2` to do this.

Specifically we'll send the parameter `u` for user and `m` for message. This means
that within our script we'll parse the data like so:

    char * user = req->getstr(req, "u", true);
    char * msg  = req->getstr(req, "m", true);

And then we'll need to somehow store it, lucky for us we have `updateConversation` 
from our internal's library to work with. The signature looks like this:

    int updateConversation(const char * user, const char * addendum)

Gosh, it's like we designed it this way or something! 

Enough chatter, let's get to the code:

_chat.h_

    #include "config.h"
    #include "chatfile.h"
    #include "load_qdecoder.h"

    /* Don't pass msg with newline or "'s! */
    static void printSuccess(int updated, char * msg){
        printf("{\"success\": %s, \"message\" : \"%s\"}", updated ? "true" : "false", msg);
    }

    int main(void){
        chatInit();
    #ifdef ENABLE_FASTCGI
        while(FCGI_Accept() >= 0) {
    #endif
        qentry_t *req = qcgireq_parse(NULL, Q_CGI_POST);
        char * user = NULL; 
        char * msg = NULL;
        qcgires_setcontenttype(req, "application/json");

        user = req->getstr(req, "u", true);
        if(user == NULL){
            /* They did not send us a proper request. */
            printSuccess(0, "Invalid Request");
            goto end;
        }
        /* Limit the user name length */
        int i = 0;
        int maxlength = 21;
        for (i = 0; i < maxlength && user[i] != '\0'; ++i)
            ;
        if(i == maxlength){
            printSuccess(0, "Username too long");
            free(user);
            goto end;
        }

        msg = req->getstr(req, "m", true);
        if(msg == NULL){
            printSuccess(0, "Invalid Request");
            free(user);
            goto end;
        }

        int updated = updateConversation(user, msg);
        printSuccess(updated, "Message has been sent");
        
        free(user);
        free(msg);
        // De-allocate memories
        end:
        req->free(req);
    #ifdef ENABLE_FASTCGI
        }
    #endif
        return 0;
    }

You'll notice this is exceptionally similar to the polling process, except that 
we do our validations a little differently. First off, there is none for the
chat message itself. Why? Because going into the minitiua of what we would actually
have to watch for is WAY too much for this blog post. Second, we are limiting the
length of the username. Why? Because I figured we had to do some type of validation 
for this script. And this code, in my estimation, is more protective than using `strlen`. 
Why? Because `strlen` relies on the string being ended properly, and we're dealing
with user input. So we assume nothing and simply count characters while checking
for the end of the string.

By this point you're probably wondering: "Why does he keep using `goto`?"

And the answer is, because it makes my code cleaner. Now before you declare a 
crusade on me for bad practice and etc, let me explain to you why `goto` is good
in this use case:

- `goto` is a local jump, it's not an actual long jump statement
- we prevent a lot of conditional branching and repeated code by using it
- it's very readable in my opinion since all the scripts are small enough to view at once
- `goto` is great for error handling since C has no conditionals

The script above can be rewritten to not use `goto`, if you want to repeat code and
nest a bunch of if conditionals inside one another. Also, the flow of the code is
logicaly structured as well.

Next up, how to test the above script? When you send a `POST` request to a server, 
a few environmental variables are set pertaining to the Content-Length, the Request
Method, and various other things. The most important thing to remember is that the
data comes in on stdin. So to test it, we need to set the proper variables and then
pipe data into our script. You can do so by running the following:

    CONTENT_TYPE="application/x-www-form-urlencoded" REQUEST_METHOD=POST CONTENT_LENGTH=11 ./bin/chat.cgi <<< "u=test&m=hi"

This will send a message of "hi" from the user "test" into the chat history in the
`DATA_FILE`. The `CONTENT_LENGTH` is **extremely** important for the inner workings
of qdecoder, and if you're testing your scripts out then make sure to set this right.
Also, when testing this out, I found that only the right `CONTENT_TYPE` would allow
qdecoder to work from the cli for postings. You can add the following to your **Makefile**
in order to automate some tests of your script:


    test-chat:
        CONTENT_TYPE="application/x-www-form-urlencoded" REQUEST_METHOD=POST CONTENT_LENGTH=7 ${valgrind} ./bash bin/chat.cgi <<< "u=12345" 
        CONTENT_TYPE="application/x-www-form-urlencoded" REQUEST_METHOD=POST CONTENT_LENGTH=23 ${valgrind} ./bin/chat.cgi <<< "u=123456789012345678901"
        CONTENT_TYPE="application/x-www-form-urlencoded" REQUEST_METHOD=POST CONTENT_LENGTH=11 ${valgrind} ./bin/chat.cgi <<< "u=test&m=hi"

**Note:**<small>You might need to set #!/bin/bash at the top of the Makefile, or change the symlink of /bin/sh to /bin/bash instead of /bin/dash if you have problems running `make test-chat`</small>


#### _Reading_

And last but not least, we have the script for reading the history file out to the
world:

    #include "config.h"
    #include "chatfile.h"
    #include "load_qdecoder.h"

    int main(void){
    #ifdef ENABLE_FASTCGI
        while(FCGI_Accept() >= 0) {
    #endif
        qentry_t *req = qcgireq_parse(NULL, Q_CGI_GET);
        qcgires_setcontenttype(req, "text/plain");

        FILE * fp =  getChatFile();
        if(fp == NULL){
            printf("%s\n", "Could not retrieve chat history. Please try again later");
            goto end;
        }

        int cOrEOF;
        char c;
        while( (cOrEOF = fgetc(fp)) != EOF){
            c = (char)cOrEOF;
            printf("%c", c);
        }
        fclose(fp);

        end:
        req->free(req);
    #ifdef ENABLE_FASTCGI
        }
    #endif
        return 0;
    }

This script is straightforward, we retrieve our chat history with the internal
function `getChatFile` and then output to the world as plain text. If we can't 
read the file we simply print out an error message. An observant reader will 
notice that we're not calling `chatInit` anywhere. We know that `chatInit` simply
creates our history file, which we're going to check for anyway when we try to
read it. So there's no point in checking twice and we skip the call to initialize.

Since we're storing the chat in the **tmp** directory (if you're using the defaults
from last tutorial and on a *nix system.) the chat will be cleared whenever you
shut off your computer at least, so people need to either poll or check the heartbeat
of your server to make sure it's initialized.

Since the read script is stateless, you don't need to worry about sending any environmental
variables when trying to test it and can simply run it with `./bin/read.cgi` after
a `make` command.

And that's it for the CGI scripts! Now we just need to set up a server:

#### Apache Configuration

So now all that we have to do is setup a new virtual host in our apache configuration
to wrap our CGI scripts. First off, if you're working locally, add this line to
yours hosts file (/etc/hosts for *nix, %systemroot%\system32\drivers\etc\ for windows)

_/etc/hosts_

    127.0.0.1 www.chat.dev

and next in your apache configuration file:

_/sites-available/default_

    <VirtualHost *:80>
            ServerAdmin webmaster@localhost
            ServerName www.chat.dev
            DocumentRoot /path/to/this/repository/tutorialchat/www
            <Directory />
                    Options Indexes
                    AllowOverride None
            </Directory>
            Alias /chat /path/to/this/repository/tutorialchat/bin
            <Directory />
                    AddHandler cgi-script .cgi
                    AllowOverride None
                    Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
                    Order allow,deny
                    Allow from all
            </Directory>
    
            ErrorLog /path/to/this/repository/tutorialchat/error.log
    
            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel warn
    
    </VirtualHost>

Note you'll need to change the path's inside the configuration to match your own
server, but it's pretty easy to do. What we've done is said that when someone goes
to `/chat/<file>.cgi` we'll let apache `ExecCGI` and run the script there. This
means that **anything** in that directory ending in **.cgi** will be able to be
seen from the outside world.

Before you restart/start your webserver we need to make the document root exist.

    mkdir wwww
    echo "<html><body><h1>I'm alive. Yay." > www/index.html

now start or restart your apache and navigate to `http://www.chat.dev` and you'll
see the words "I'm alive. Yay." on the screen. If you navigate to `http://www.chat.dev/chat/heartbeat.cgi`
you should be greeted with the familiar:

    { "heartbeat" : 1408623802, "initialized" : true }

which let's you know that your chat server is up and ready for an interface.




[Harp]:http://harpjs.com
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[xampp]:https://www.apachefriends.org/index.html
[wamp]:http://www.wampserver.com/en/
[their instructions]:https://github.com/wolkykim/qdecoder
[examples]:http://www.qdecoder.org/releases/current/examples/
[from here]:https://github.com/wolkykim/qdecoder
[google fu]:http://lmgtfy.com/?q=qdecoder+windows
[documentation]:http://wolkykim.github.io/qdecoder/
[valgrind]:http://valgrind.org/