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
in the last tutorial</b>, and it's always a good idea to do so.

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
        qentry_t *req = qcgireq_parse(NULL, 0);
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
- Reading: Retrieve the current chat history
- Writing: Send a message to the chat server

#####Polling

Let's define our contract: The user will send us a timestamp of when they last
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

    {"updated": true}










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
