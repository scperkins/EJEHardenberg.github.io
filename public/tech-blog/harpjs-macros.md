###HarpJS Macros and Multiple Static Domains

I very recently bought my new domain name and redesigned my website. I'm still using [Harp] to 
generate my site, and [apache] to serve it.

Any good web developer worth their salt will tell you that if you've got static
content, you'll do the internet and your site visitors a favor if you use the
proper cache headers. This isn't a cache header tutorial though, instead, I'd like
to show you how you can create a powerful Macro on your Harp Site to enable proper
CDN/static domain usage for any static content you might have. 

If you don't know what I'm talking about, you've probably seen things like 
[https://fbstatic-a.akamaihd.net/rsrc.php/v2/yL/r/f2IiBfPD5Mj.png]
or things like `somesites.static.1.domain.com`. The use of static, cookieless, 
subdomains as hosts for resources like images, javascript, or css is something
that enables browsers to download and display a webpage faster. Your browser is
able to download a site faster (in general) if it can open up connections to 
multiple hosts. I won't go into all the details, you can always read [wikipedia]
for that.

As a case study, I'm going to tell you how it's done on this site. I assume you're
somewhat familiar with Harp, and if not I recommend checking out their excellent [documentation].

First, HarpJS runs as a [Node] module and is part of the new-fangled server-side
javascript paradigm. As such, we get to use things like EJS to use Javascript to
generate our pages in a similar way to PHP. Something that isn't immediately obvious 
from following the many [good recipes] on Harp's site is that full blown javascript 
means _full_ _blown_ _javascript_. This means functions my friends! 

The best way to enable any image to be served from our static subdomain is to write
what I would call a Macro (I've been in the C world recently, don't mind my jargon).
This macro is pretty simple and uses a couple globals that we'll declare in our 
harp.json file like so:


	{
		"globals" : {
			"macros" : {},
			"nextDomain" : 0,
			"maxDomains" : 8,
			"staticimagesurl" : [
				"static.ethanjoachimeldridge.info", 
				"static1.ethanjoachimeldridge.info", 
				"static2.ethanjoachimeldridge.info",
				"static3.ethanjoachimeldridge.info",
				"static4.ethanjoachimeldridge.info",
				"static5.ethanjoachimeldridge.info",
				"static6.ethanjoachimeldridge.info",
				"static7.ethanjoachimeldridge.info"
			]
		},

	}

Each of the `staticimagesurl` will function as one of our 'cdn' servers. If you're
using S3, CloudFlare, or MaxCDN then you'd be replacing each of those items with 
your corresponding urls. The `maxDomains` field could be replaced by an array length
check during our macro, but for this case I figured it's simple enough to just count
them myself. 

With our globals in place, we can write our function, to make it accessible to all
pages, I created a partial for it that can be easily injected wherever I need it:

####macros.ejs

	<%
	macros.rrImageDomain = function rrImageDomain(){
		//Round robin style
		//You could also do staticimagesurl[Math.floor(Math.random() * staticimagesurl.length)]; for random urls
		return staticimagesurl[nextDomain++ % maxDomains];
	}
	%>

 Simply put, we are adding a function to the global macros object. Within this macro
 we are using our list of static content domains and whenever we call the macro
 we'll output the next item in the list (wrapping around when nextDomain is greater
 than 7). This will set us up to distribute the requests evenly over the static
 content servers.

 To use the macro we can do this (From one of my _layout files):


	 <%- partial('_shared/macros') %>
	<!DOCTYPE HTML>
	<html>
		<head>
			<title>Ethan J. Eldridge | <%= title %></title>
			<!-- snip -->
	    	
			<link rel="shortcut icon" href="//<%= macros.rrImageDomain() %>//favicon.ico" type="image/x-icon" />
			<link rel="icon" href="//<%= macros.rrImageDomain() %>//favicon.ico" type="image/ico">

This will result in the following markup:

<!DOCTYPE HTML>
<html>
	<head>
		<title>Ethan J. Eldridge | Ethan Joachim Eldridge&#39;s Webspace</title>
    	<!-- snip -->

		<link rel="shortcut icon" href="//static6.ethanjoachimeldridge.info/favicon.ico" type="image/x-icon" />
		<link rel="icon" href="//static7.ethanjoachimeldridge.info/favicon.ico" type="image/ico">

You can see that we simply have incrementing subdomains for our static content (in this case, domains 6 and 7)

By using macros like this it is easy to generate a site that is not only fast to 
serve (due to the static content itself), but also fast to load (due to leveraging
the browsers ability to download images in parallel from multiple hosts). Feel free
to leave questions or comments in the disqus thread below!




[Harp]://harpjs.com
[Node]:http://nodejs.org/
[apache]:https://httpd.apache.org/
[good recipes]:http://harpjs.com/recipes/
[https://fbstatic-a.akamaihd.net/rsrc.php/v2/yL/r/f2IiBfPD5Mj.png]:https://fbstatic-a.akamaihd.net/rsrc.php/v2/yL/r/f2IiBfPD5Mj.png
[wikipedia]:http://en.wikipedia.org/wiki/Content_delivery_network
[documentation]:http://harpjs.com/docs/