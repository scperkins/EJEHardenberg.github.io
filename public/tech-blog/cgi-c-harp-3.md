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

####Some basics in Harp

With that, we have every file we need for our chat server. Let's do a basic "Hello World"
for harp now to verify that everything is working properly. First off, we need to 
define the layout of our page. To quote [harp's layout documentation]

<q>A Layout is a common template that includes all content except for one main content area. You can think of a Layout as the inverse of a partial.</q>

in other words, your layout defines the parts of your website that don't change from
page to page. With harp, you can specify layout's for different pages, or even tell
it to not use one at all. By default, Harp will look for a file named **_layout**
with an extension it recognizes (_.ejs_, _.jade_, _.html_).

Now that I've mentioned layout's it bears to say that I should mention partials as 
well. We're not using any here for our small site, but if you're going to learn about
Harp, by jove you're going to learn about [partials]! A partial is similar to a php
script that is `include`'d into another script. Within a Harp template you can use
the following ejs or jade to bring in another harp file:

    <%- partial("_header") %> //in .ejs
    != partial("_header") //in jade

It's also possible to pass parameters to your partials, but you can check out the
excellent documentation on [partials] to read about that. Just becuase you're writing
an ejs file does not mean you can't include a jade file. That's one of the beauties
of harp, you can mix and match and get what you expect.

Next up on our list of basics, data files! Harp supports two data files, **harp.json**
and **_data.json**. The file we'll be using is **harp.json*, which is a global data
file accessible from your code anywhere in your ejs or jade files. You cannot access
this or any other data object within markdown, html, or any other file besides those
two. Since **harp.json** is a global data sheet, that means **_data.json** is ...
you guessed it, a data file specific to something. Specifically, each directory
can have one copy of **_data.json** with an object of objects stored in the lovely
JSON format.

Something you might have noticed about harp filenames is that a few I've mentioned
start off with an underscore. This isn't an accident. Any file you start with `_`
will be ignored when harp looks to display files. This means that a file `_index.html`
will not be shown to the user even if they navigate to the URL where you'd expect it.
This doesn't just apply to files though, you can start directory names with one
and harp won't allow public access to anything inside. This isn't to say that harp
itself can't get to them though. In fact, the common usage of the underscore, besides
the **_data.json** files are to store things like partials, headers, or other 
repeatable code that occurs in multiple templates.

We only need one more tool in our arsenal before we can get to the code. The ability
to render content within a layout. This is done by the use of the `yield` variable.
You can read all the nitty gritty about [yield here], but it's actually quite 
simple to use and understand. It's a variable that contains the contents of whatever
you're trying to view. If you've navigated to a directory, the index pages contents
will be inserted into the `yield` variable. Gone to a blog post? That information
you want to share is in the variable. Simple.

With all of that out of the way, this is what our **harp.json** file looks like:

_harp.json_

	{
		"globals" : {
			"title" : "Temporary Chat",
			"description" : "Chat with whoever is online, yourself, or nobody! A sample chat server made in a tutorial by Ethan Joachim Eldridge",
			"chatdomain" : "//www.chat.dev/chat"
		}
	}

We've defined the global properties of our website. Besides the `globals` field 
all of these properties are arbitrary. You can store whatever you normally store
into a JSON object for use in your site. On my own site I store CDN url's, macro functions,
and even a list of projects. For our server, we've created a sitewide title and description
as well as defined a `chatdomain`. This domain is going to be a property we use
in our javascripts to tell the front end where to submit requests to. 
**Note**: Readers of the [previous post] will note that `chatdomain` is our CGI URL.



####Designing our interface

####Using Pure CSS

####Connecting Front to Back





[Harp]:http://harpjs.com
[harp's quickstart page]:http://harpjs.com/docs/quick-
[partials]:http://harpjs.com/docs/development/partial
[their download page]:http://nodejs.org/download/
[harps layout documentation]:http://harpjs.com/docs/development/layout
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[first post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-2
[pure]:http://purecss.io/
[jquery]:http://jquery.com/
[yield]:http://harpjs.com/docs/development/yield