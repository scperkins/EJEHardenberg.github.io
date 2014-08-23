###CGI with Harp and C - Web front end for the Chat Server

If you haven't read the [first post] or the [previous post] you might want to do 
that before starting this one! If you're looking for the source code for the finished
project, you can find that [here on github] in my repositories.

####The Plan

In this post we're going to install [Harp], and I'll show you some quick tricks 
and recipes in making our site look decent. Once the layout is in place we'll connect
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
and **_data.json**. The file we'll be using is **harp.json**, which is a global data
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
into a JSON object for use in your site. On my own site [I store CDN] url's, [macro functions],
and even a list of projects. For our server, we've created a sitewide title and description
as well as defined a `chatdomain`. This domain is going to be a property we use
in our javascripts to tell the front end where to submit requests to. 

**Note**: Readers of the [previous post] will note that `chatdomain` is our CGI URL.

Our layout is going to be pretty generic, but we don't need much for this:

    <!DOCTYPE html>
        <head>
            <title><%= title %></title>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <meta name="description" content="<%= description %>" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="stylesheet" type="text/css" href="/style.css">
        </head>
        <body>
            <%- yield %>
        </body>
        <script type="text/javascript">
            /* Globals for use by the scripts */
            window.chatdomain = "<%= chatdomain %>"
        </script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script type="text/javascript" src="/chat.js"></script>
    </html>


So here we have our first ejs file, if we want to output some variable we wrap it
in `<%` and `%>` tags. Once we do this harp will lookup our variable for us and 
spit it out (provided it exists). When harp performs a lookup, any data in the
current directory's **_data.json** file will override anything in the **harp.json** 
global file. This is useful for having a fall back title in your global and then
having specific ones for each page of your site. 

In our case, we are spitting out a global javascript variable `chatdomain` and 
attaching it to the window object of the browser. This will allow any of our 
javascript files to use the URL stored in **harp.json** to find out where the CGI
server is. We're also using [cloudfare's javascript] CDN to get jquery onto our 
site without having to download anything to any local environments. 


####Designing our interface

Most people in their twenties know what a chatroom looked like, after all, before
we had Facebook and g+ we had AIM, IRC, and chatrooms everywhere. The internet was
a wild place of pop-up ads, too many windows open, and being constantly asked for your A/S/L.
There's less of that now, but the interface to a chat still typically looks something like 
this:

<img src="/images/tech-blog/chat-diagram.png" width="500px" height="400px" style="padding-left: 25%;">

We're going to make something similar to this, in that we'll have a main window
area to display the current chat going on, and a dialog box of some kind to send
messages. Don't worry it will have a _much_ better color scheme and presentation.
I promise. That said, let's get some code onto the screen:

_index.ejs_

    <header>
        <h1><%= title %></h1>
        <small>Talk to random people, you never know who you'll talk to!</small>
    </header>
    <section>
        <form action="/chat/chat.cgi" method="POST">
            <input name="u" placeholder="Enter your chat handle">
            <button>Send</button>
            <label>
                <small>Press Enter to Send</small>
                <input type="checkbox" name="entersend"  />
            </label>
            <textarea name="m" placeholder="type your message here and press send"></textarea>
            
        </form>
    </section>
    <section>
        <div id="history">
            <marquee>Loading</marquee>
        </div>
    </section>

When rendered in a browser we get a bundle of elements on our page:

<img src="/images/tech-blog/elements-of-chat.png" width="544" height="198" style="padding-left: 25%" />

Yes, we're using a marquee tag. Why not? I like to have some fun with my HTML. And
sadly, the [blink tag] is deprecated. It makes a decent loading animation if you
don't want to use something like [this] to make a nice loading image. Note that
our form is posting to our CGI script that will create a message for us. We've
also put a send button in place, as well as the option to use enter to send instead
of pressing the button. We'll wire this whole thing up after we've made it acceptable
to look at.

####Styling our site

One of the many reasons I use [Harp] is for the native [less] support. I love being
able to write my CSS in a hierarchical way. If you haven't used [less] before, 
there's no reason to fear! I'm sure you'll understand it with just a single glance 
at it:

    @bgcolor: #F24E20;

    html{
        font-family: Georgia, Serif;
        background-color: lighten(@bgcolor, 10);
    }
    body{
        margin: 0 auto;
        text-align: center;
        width: 60%;
        background-color: @bgcolor;
        border-radius: 2em;
        header{
            width: 100%;
            padding: 0;
            background-color: darken(@bgcolor, 20);
            h1{
                padding-bottom: 5px;
                margin-top: 0px;
                margin-bottom: 0px;
            } 
            small{
                display: block;
                width: 100%;
                padding-top: 5px;
                font-style: italic;
                background-color: darken(@bgcolor, 10);
            }
        }
        section{
            width: 100%;
            form{
                padding-left: 10%;
                width: 80%;
                input,textarea{
                    width: 100%;
                    display: block;
                }
                textarea{
                    min-height: 60px;
                }
                label{
                    input{
                        vertical-align: middle;
                        display: inline-block;
                        width: auto;
                    }
                }
            }
            #history{
                min-height: 400px;
                background-color: #eee;
                width: 80%;
                margin-left: 10%;
                margin-top: 10px;
                margin-bottom: 10px;
                padding-bottom: 10px;
                div{
                    min-height: 400px;
                    display: block;
                    width: 100%;
                    
                    overflow: auto;
                }
            }
            padding-bottom: 10px;
        }
    }

    button {
       border-top: 1px solid #f797bf;
       background: #d66585;
       background: -webkit-gradient(linear, left top, left bottom, from(#9c3e78), to(#d66585));
       background: -webkit-linear-gradient(top, #9c3e78, #d66585);
       background: -moz-linear-gradient(top, #9c3e78, #d66585);
       background: -ms-linear-gradient(top, #9c3e78, #d66585);
       background: -o-linear-gradient(top, #9c3e78, #d66585);
       -webkit-border-radius: 15px;
       -moz-border-radius: 15px;
       border-radius: 15px;
       -webkit-box-shadow: rgba(0,0,0,1) 0 1px 0;
       -moz-box-shadow: rgba(0,0,0,1) 0 1px 0;
       box-shadow: rgba(0,0,0,1) 0 1px 0;
       text-shadow: rgba(0,0,0,.4) 0 1px 0;
       color: white;
       text-decoration: none;
       vertical-align: middle;
       }
    button:hover {
        cursor: pointer;
        border-top-color: #28597a;
        background: #28597a;
        color: #ccc;
       }
    button:active {
       border-top-color: #1b435e;
       background: #1b435e;
       }

A couple things, you can pretty much ignore the button css, all of that was 
[generated here] because I'm too lazy to spend a lot of time on a gradient. But
the rest of the code is all mine and yours. The color theme exists to show you
that the `darken` function of less is very cool. Also, you'll notice that we have
a variable controlling the color scheme of the page. Variables in less begin with
an `@` sign, and are declared the same as other CSS properties, like so:

    @somevar: sameval;

Another thing to notice is the nesting of elements, this is the hierachical structuring
of less that I was talking about. It is very intuitive to follow that the CSS rules
apply with the cascade of nesting and only there. Writing the same thing in plain
CSS would take a good amount more code and be far less readable. Also, harp minifies
your assets for you, so you don't have to go to an outside tool for that either!

Once the above css is in place, the chat screen will now look like this:

<img src="/images/tech-blog/chat-styled.png" width="600px" height="362px" style="padding-left: 25%">

Which is far better than a mess of elements on the screen. It's certainly not the
most beautiful thing in the world, but it's good enough for this tutorial. We're
almost done with our chat server now! We just need to wire the components up!

**Note:** <small>if you want to run your website with harp and tweak the styles, you 
can use `harp server` from the root of the project to run a local server on port 9000</small>


####Connecting Front to Back

The last thing we need to do is handle the javascript talking to our CGI scripts.
The high level view of what we're going to do is the following:

- check that the server is online
- poll the server for updates
- create a user handle and keep it
- send a message
- recieve all messages

This is not an extensive list of things to do, so let's dive in:

##### Some setup

_chat.js_

    jQuery( document ).ready(function( $ ) {
        var heartbeatURL = window.chatdomain + "/heartbeat.cgi"
        var pollURL = window.chatdomain + "/poll.cgi"
        var readURL = window.chatdomain + "/read.cgi"
    })

Remember **chat.js**? We created this file at the beginning of this tutorial, and
now it's time to fill it out. We define a couple convenience URL's so that we 
can easily change them if the scripts change. This is why we attached the chatdomain 
to the window object, so we could grab it easily here.

##### Checking the pulse of the server

To make sure we have a connection to the server we can poll out heartbeat script 
and check the `initialized` field of the returned object. If this is false we know
something is up and we shouldn't allow the user to do anything:

    Content-Type: application/JSON

    { "heartbeat" : 1408764565, "initialized" : true }

If we get a response like the above then we know we're still connected and don't
need to disable the chatting functions of the server.



[cloudfare's javascript]:http://cdnjs.com/
[Harp]:http://harpjs.com
[harp's quickstart page]:http://harpjs.com/docs/quick-
[partials]:http://harpjs.com/docs/development/partial
[their download page]:http://nodejs.org/download/
[harps layout documentation]:http://harpjs.com/docs/development/layout
[qdecoder]:http://www.qdecoder.org/wiki/qdecoder
[here on github]:https://github.com/EJEHardenberg/chat-tutorial
[first post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-2
[jquery]:http://jquery.com/
[yield here]:http://harpjs.com/docs/development/yield
[I store CDN]:http://www.ethanjoachimeldridge.info/tech-blog/harp-macro-revisit
[macro functions]:http://www.ethanjoachimeldridge.info/tech-blog/harpjs-
[blink tag]:https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blink
[this]:http://ajaxload.info/
[less]:http://lesscss.org/
[generated here]:http://css-tricks.com/examples/ButtonMaker/#