###CGI with Harp and C - Web front end for the Chat Server

If you haven't read the [first post] or the [previous post] you might want to do 
that before starting this one! If you're looking for the source code for the finished
project, you can find that [here on github] in my repositories.

####The Plan

In this post we're going to install [Harp], and I'll show you some quick tricks 
and recipes in making our site look decent. Also, we'll also use [pure] css to
have a decent looking base css file. Once the layout is in place we'll connect
the front end to the backend with some simple javascript using [jquery]. 

####Install Harp

The first we need to do is install harp onto our machines. Harp runs using Node,
so we need to have that installed first. If you're using linux you can use `apt-get`
or some other package manager to install Node and `npm`, if you're on windows
then you can download Node from [their download page]. 

Once you have `npm` installed you can then follow the simple instructions on 
[harps quickstart page] to install it. To save you the click all you need to do
is run:

    npm install -g harp

**Note**: If you're on windows Node comes with a command prompt you can do to run
this, if you're on a *NIX system you can run the above on your terminal (might
require sudo).

You've installed harp so now run the following commands to setup our website structure:

    mkdir public
    touch public/chat.js
    touch public/style.less
    touch public/_layout.ejs
    touch public/index.ejs
    touch harp.json

With that, we have every file we need for our chat server. Let's do a basic "Hello World"
for harp now to verify that everything is working properly. First off, we need to 
define the layout of our page. To quote [harp's layout documentation]

<q>A Layout is a common template that includes all content except for one main content area. You can think of a Layout as the inverse of a partial.</q>

in other words, your layout defines the parts of your website that don't change from
page to page. With harp, you can specify layout's for different pages, or even tell
it to not use one at all. By default, Harp will look for a file named **_layout**
with an extension it recognizes (_.ejs_, _.jade_, _.html_) and use that. 



####Designing our interface

####Using Pure CSS

####Connecting Front to Back





[Harp]:http://harpjs.com
[harp's quickstart page]:http://harpjs.com/docs/quick-start
[their download page]:http://nodejs.org/download/
[harps layout documentation]:http://harpjs.com/docs/development/layout
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[first post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-2
[pure]:http://purecss.io/
[jquery]:http://jquery.com/