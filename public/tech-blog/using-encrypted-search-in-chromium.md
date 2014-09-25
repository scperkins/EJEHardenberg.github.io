###Using Encrypted search in chrome. 


Today, while reading [this post about how SSL isn't a performance
problem anymore], I discovered a new tool: [encrypted google search].
Thinking to myself that this was a great thing to have handy, I decided
to go ahead and make it my default search engine. 

####How to do it

These instructions are for Chromium 33.0.1750.152 because that's what
I'm running, but I imagine that they're extremely similar to any other
chrome based browser. First off, open up your settings at
[chrome://settings/]. If this doesn't work, look in any of the dropdown
menus for something saying settings. 

Once you've got settings open find the Search section and click 'manage
search engines', doing so will pop open a big box with lots of ways you
can search the web. Most likely, your default is set to google. Also,
you'll notice a huge bunch of letters and whatnot in a url-looking thing
in the third column. This is what we're changing. Right now, all your
information about your browser, version number, and whatever else is
sent up to the google mothership. So change this to the following:

    https://encrypted.google.com/#q=%s

Simple right? The `%s` is where your search query will be replaced. This
is what it should look like:

<img src="/images/tech-blog/search-engine.png" width="716px" height="461px" />

####Why is it secure? 

First off, we can tell something immediatly by the URL. The use of the
\# (which is a fragment of a url) gives us good indication about what's
just been sent to the server. Specifically, anything after the \# is
not. Why? This is just the way URL's work, fragments are used to jump to
parts of pages (like on wikipedia when you click something in the table
of contents), because they're only meant for use within the browser, the
fragments are never sent to the server at all. 

What this means is that your query is not included in the URL of the
page you're viewing. This is better because if someone is sniffing your
packets or monitoring traffic, or even just looking at accesslogs, they
can see what you were searching for. Obviously you're still doing a
search, so how are we doing it?

Inspecting the network panel you'd notice that those requests are still
going out with your search terms in them. So that made me wonder, if
everything is in the URL still, going somewhere, then why is this any
better? Turns out someone [already asked], and if a site that you click
on isn't using HTTPS, then they won't recieve any additional information
besides the fact that you came from google. 

This means google is still mining your searches and tayloring everything
to your needs (which you probably enjoy despite the semi-creepiness of
it sometimes), but if someone isn't respecting your decision to surf the
web under SSL, they don't get to know about you until they shape up. 

Ironically enough, this site isn't hosted under SSL, nor is it likely to
be anytime soon. (SSL certificates cost a lot of money). So while I use
google analytics to try to guage what I should write about next, I'll
never know why you got to my site if you're using the encrypted google
search. 

Anyway, stay safe, search secured, and never let a hacker sniff your
packets without proper protection!

[already asked]:http://security.stackexchange.com/questions/32367/what-is-the-difference-between-https-google-com-and-https-encrypted-google-c
[chrome://settings/]:chrome://settings/
[this post about how SSL isn't a performance problem anymore]:https://www.imperialviolet.org/2010/06/25/overclocking-ssl.html
[encrypted google search]:https://encrypted.google.com
