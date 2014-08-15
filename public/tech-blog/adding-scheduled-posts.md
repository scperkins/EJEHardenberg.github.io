### Draft and Scheduled Posts in Harp

If you use [Harp], you've probably checked out their recipes before. And if you've
looked at those recipes you've probably seen the [great draft recipe] about draft
posts. I'm not going to try to do a better job than Kenneth Ormandy on drafts so
you can read that post there if you'd like. What I am going to show you in this
recipe, is how to schedule your blog posts, pages, or anything else your heart
desires.

So let's get down to what we need, as usual I'm going to be using my own site as
an example of how all this works. We'll need a few things:

 - _data.json
 - _layout.ejs
 - Sitemap.xml.ejs 

If you don't have a Sitemap, then you can ignore that part later, but if you want 
to make yourself one [you can read how to here]. 

In simple terms, we're going to attach a `date` meta property to your blog posts
and then use that to decide when the post will be available on your blog. The code
to support this is pretty simple. We'll then update the Sitemap to filter out any
posts that shouldn't be available yet. After all, you don't want those search 
engines reading content they shouldn't yet!

####Step one - Make a site

    mkdir yoursite
    cd yoursite
	harp init
	touch example.md && echo "1" >> example.md
	touch in-the-past.md && echo "2" >> in-the-past.md
	touch in-the-future.md && echo "3" >> in-the-future.md


Running the above steps will make the default harp project structure, as well as
a few example blog posts to illustrate the scheduling. We'll modify those in a 
moment, but first:

####Step two - Create _data.json

    {
        "example" : {
                "title" : "Blog Post 1",
                "date"  : "2014-08-13"
        },
        "in-the-past" : {
                "title" : "Blog Post 0",
                "date" : "2014-07-24"
        },
        "in-the-future" : {
                "title" : "Future Post!",
                "date" : "2015-09-14"
        }
    }

We've defined our blog posts to have a title and a date. You can probably already 
see where this is going, but let's go ahead and modify the index file appropriately
to handle these posts:

####Step Three - Your index page

##### Change index.jade into index.ejs

    mv index.jade index.ejs

##### Change the contents of index.ejs

	<h1> Welcome to Harp.
	<h3> This is yours to own. Enjoy.

	<%
	for(idx in public._data){
	    post = public._data[idx]
	    if(new Date(post.date) <= new Date()){
		%>
		<h2><a href="/<%- idx %>"><%- post.title %></a>
		<%
	    }
	}
	%>

This code simply makes a list of links to the blog posts if their publish date is 
in the future. Note that this doesn't stop your layout from rendering the items, 
so someone can still access a future post by going to /in-the-future right now.

####Step Four - Protect the Future

In order to not have the above happen, you need to modify your layout file to go
from this:

__layout.jade_

	doctype
	html
	  head
	    link(rel="stylesheet" href="/main.css")
	  body
	    != yield

To this:

__layout.ejs_

	<DOCTYPE html>
	  <head>
	    <title>Your site</title>
	    <link rel="stylesheet" href="/main.css">
	  </head>
	  <body>
	    <% var obj = public._data[current.source] %>
	    <% if( !obj  || (obj.date && new Date(obj.date) <= new Date()) || environment == "development" ){ %>
	    <%- yield %>
	    <% } else { %>
	    <%- partial("404") %>
	    <% } %>

We loop through our meta data, and if we don't have any object defined, we know
that that's our index file, so we should display it. If we do have some data 
defined, then we check if it should be published or not. Lastly, when you're
working on something locally, you'll likely want to view it before it goes live.
This is why we specify that it's ok to show the content if the `environment == "development"`

If you want, right now you can modify index.ejs's

    if(new Date(post.date) <= new Date()){

line to 

     if(new Date(post.date) <= new Date() || environment == "development"){

to let your future blog posts show on the index page if you're working locally 
as well.

I use `.ejs` files due to personal preference, but it's possible to do the same
thing as I did above with jade if you want to, though that's an exercise for the
reader. ;)


#### Step 5 - Protect your SEO! (Sitemap update)

If you don't have a sitemap you can [make yourself one] and then come back, or 
you can skip this section. The sitemap code is simple and we only need to change
one part. Find the code that looks like this:

	if(head['_data']){
		obj = head['_data'][file]
		if(obj && obj.date){
			date = new Date(Date.parse(obj.date)).toISOString()
		}
	}

and add a small conditional to skip over any posts that are drafts or shouldn't be
displayed:

	if(head['_data']){
       	obj = head['_data'][file]
       	if(obj && obj.date){
       		if(new Date(obj.date) > new Date()){
       			continue;
       		}
       		date = new Date(Date.parse(obj.date)).toISOString()
       	}
    }

Also, you'll want to make sure the `_data.json` file has the following added to it:

    
	"Sitemap" : {
		"layout" : false
	}

Otherwise you'll get XML format issues due to the html layout.

#### Final Step - Miscellaneous auto-building

If you're deployed your site to [the harp platform] then you're done. If you're
deploying just your static files to something like [gh-pages] or Apache you'll 
need some type of automatic build process to keep your site's pages publishing
on schedule. For that I recommend something like

    5 0 * * * * /path/to/your/directory/publish.sh

Where publish.sh is:

    #/bin/sh
    cd /path/to/your/directory/
    harp compile

And then you'll be compiling harp every day at 5 minutes after midnight. If you use
gh-pages you'll probably want to add this cron task locally, if it's on a server
then you'll want to do it up there. All in all it's pretty simple to add scheduled
posts to your blog or site! 



[Harp]:http://harpjs.com
[great draft recipe]:http://kennethormandy.com/journal/static-draft-posts-with-harp
[you can read how to here]:http://www.ethanjoachimeldridge.info/tech-blog/xml-sitemap-for-harpjs
[make yourself one]:http://www.ethanjoachimeldridge.info/tech-blog/xml-sitemap-for-harpjs
[the harp platform]:https://www.harp.io/
[gh-pages]:https://pages.github.com/