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

If you're on windows you can download a bundle like [xamp] or [] and install the
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
sure everything is working. Once you've got that come back here.

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
much more than this so it's a pragmatic choice. 

...

[Harp]:http://harpjs.com
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[xamp]:
[]:
[their instructions]:
[examples]:http://www.qdecoder.org/releases/current/examples/
[from here]:https://github.com/wolkykim/qdecoder
[google fu]:http:// let me google that for you search for qdecoder windows
[documentation]:http://wolkykim.github.io/qdecoder/