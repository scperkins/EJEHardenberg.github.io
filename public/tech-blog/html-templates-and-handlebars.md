This post is by no means a tutorial, just chronocling my short adventure into HTML templates tonight. 
------------------------------------------------------------------------

I've just started playing around with HTML templates. It took me a small
amount of searching for the right tutorials, but after a while I found 
a couple that when I combined them it all started worked together nicely. `

[HandleBars](handlebarsjs.com) is pretty simple to use. Stare at the 
documentation and syntax for a while, then realize that yes, if you want
to do anything 'fancy' like `if(a==b)` that you'll need to write your own
helper. But, if you're just looking for some simple and easy to use
templating, it's great. 

I knew from the start, that I wanted to include my templates from seperate
files. It didn't make much sense to me to put the template directly into
my source code files, since the only things I wanted to template for were
items that would appear across multiple pages and it makes sense then to
push the templates into their own files for that. So I decided to include
jQuery into my project so I wouldn't spend a lot of time writing javascript
ajax boilerplate code.  

The `.load()` function turned out to be very useful. Since I could point it
to a url and then simply use a callback function once it was done. After
a few false starts (such as realizing that `if(a==b)` was beyond Handlebar's
abilities) I got a template spitting information out onto the page. 

From there, I moved the data itself into it's own file that I loaded again, 
with `.load()`. Figuring that if I make a backend API to power my small
project I'm starting on, that abstracting the data into it's own areas 
accesible via URL now, will turn out to be good foresight later on. 

We'll see what else comes of it. Oh, the best thing about HandleBar is 
that you can _precompile_ your templates, which means that when you're
creating dozens of templated items, that you can save yourself a good 
amount of processing time just by compiling early and not for each
instance of your templated data.