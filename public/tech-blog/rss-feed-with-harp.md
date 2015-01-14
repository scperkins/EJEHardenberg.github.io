### Creating your own RSS feed with HarpJS

A lot of people use RSS feeds to aggregate content they want to know 
about, and by offering this service from your own website or blog you 
can help distribute your content a little bit easier to the tech-savvy 
world. The other day one of my friends asked me if **my** website had an 
RSS feed. 

It does now. And I'm going to show you how to do get your own.

As you know if you've read my [previous posts] I use [HarpJS] to compile 
my website whenever I create new content. Harp let's you use EJS or Jade 
to template your website and supports a lot of different content types 
out of the box. Specifically, I write everything in [markdown] because I 
love it, and luckily for you and your RSS feed, Harp supports creating 
XML documents as well, including templating.

This is the full code that generates [my RSS feed], obviously these types 
of things depend on the data you have constructed. In my case, each blog 
post's meta data (within `_data.json`) includes a title,description, and 
date already. When I create a new post I add it to the _bottom_ of my list, 
which means that to show a listing of each, with the latest at the top, 
I have to reverset the list first before I use it:

	<?xml version="1.0" encoding="utf-8"?>
	<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
		<channel>
			<%
			var articles = [] 
			var highestDate = 0;

	      	for (var slug in public["tech-blog"]._data) { 
	            public["tech-blog"]._data[slug].slug = slug

	            if (slug != "index" && slug != "feed" && !public["tech-blog"]._data[slug].draft) {
	            	var obj = public["tech-blog"]._data[slug]
	            	obj.slug = slug
	          		articles.push(obj)  
	          		if (highestDate < Date.parse(obj.date)) {
	          			highestDate = Date.parse(obj.date)
	          		}
	        	}
	      	};
			articles.reverse()
			%>

			<title>Ethan's Techblog Feed</title>
			<link>http://ethanjoachimeldridge.info/tech-blog/feed.xml</link>
			<description>XML RSS 2.0 feed for Ethan Eldridge's tech blog</description>
			<managingEditor>ejayeldridge@gmail.com (Ethan Eldridge)</managingEditor>
			<webMaster>ejayeldridge@gmail.com(Ethan Eldridge)</webMaster>
			<lastBuildDate><%= new Date(highestDate).toGMTString() %></lastBuildDate>
			<language>en-us</language>
			<atom:link href="http://ethanjoachimeldridge.info/tech-blog/feed.xml" rel="self" type="application/rss+xml" />

			<% for (articleIdx in articles) { %>
			<item>
				<title><%- articles[articleIdx].title %></title>
				<link>http://ethanjoachimeldridge.info/tech-blog/<%= articles[articleIdx].slug %></link>
				<guid>http://ethanjoachimeldridge.info/tech-blog/<%= articles[articleIdx].slug %></guid>
				<pubDate><%= new Date(Date.parse(articles[articleIdx].date)).toGMTString() %></pubDate>
				<description>
					![CDATA[<%- articles[articleIdx].description.trim()
						.replace(/[\u00A0-\u9999<>\&]/gim, function(i) {
							if(i.charCodeAt(0) == '<'){
								console.log(i)
							}
	   						return '&#'+i.charCodeAt(0)+';';
						}).replace(/&/gim, '&amp;') 
					%>]]
				</description>
			</item>
			<% } %>
		</channel>
	</rss>

Next, the `xml`,`rss`, and `channel` elements are part of the [standard] 
and easily implemented using the examples they give you. Same with the 
feed description itself with the title, link, and editor tags. There are 
only two items that stood out when creating this feed.

#### The timestamps for date.

The date's need to be valid [RFC 822] timestamps. This means _GMT_ time. 
If I were to not call the `toGMTString()` function on my dates, then I 
would have an invalid feed because I'd get things like this:

    Fri Dec 19 2014 08:41:43 GMT-0500 (EST)

Instead of formats like this:

    Fri, 19 Dec 2014 13:42:05 GMT

If you're using something like [FeedValidator] to make sure your feed is 
[valid], then it will complain unless you use the GMT versions.

#### Links in the Description tag 

In your RSS feed, if you're going to put more than just text, you need to
encode the entities of the data and put them into a `CDATA` block. The 
spec page links to [how to format] your links, but to do it you need some 
tomfoolery with javascript. Namely this:

	<description>
		![CDATA[<%- articles[articleIdx].description.trim()
			.replace(/[\u00A0-\u9999<>\&]/gim, function(i) {
				if(i.charCodeAt(0) == '<'){
					console.log(i)
				}
					return '&#'+i.charCodeAt(0)+';';
			}).replace(/&/gim, '&amp;') 
		%>]]
	</description>

This replaces all the unicode characters (outside of 127 range) with 
their corresponding character code, then turns them into entities. There 
is a [stackoverflow] post describing this in more detail. However, the 
answer doesn't mention the `.replace(/&/gim, '&amp;')` part, only the 
[fiddle] does.

Once you have these two gotchas under control then you'll be happily displaying 
your shiny valid RSS feed image in no time!

<a href="http://feedvalidator.org/check.cgi?url=http%3A//ethanjoachimeldridge.info/tech-blog/feed.xml"><img src="/images/tech-blog/valid-rss-rogers.png" alt="[Valid RSS]" title="Validate my RSS feed" /></a>

[fiddle]:http://jsfiddle.net/E3EqX/13/
[stackoverflow]:http://stackoverflow.com/questions/18749591/encode-html-entities-in-javascript
[how to format]:http://cyber.law.harvard.edu/rss/encodingDescriptions.html
[RFC 822]:http://www.w3.org/Protocols/rfc822/
[standard]:http://cyber.law.harvard.edu/rss/rss.html
[previous posts]:harp-and-smut.html
[HarpJS]:http://harpjs.com
[markdown]:http://daringfireball.net/projects/markdown/syntax
[my RSS feed]:feed.xml
[FeedValidator]:http://feedvalidator.org/
[valid]:http://feedvalidator.org/check.cgi?url=http%3A//ethanjoachimeldridge.info/tech-blog/feed.xml
