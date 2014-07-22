###Harp Image Macros Revisited

A while ago I [wrote a blog post on using a CDN and Harp together] and gave out
this piece of code

	<%
	macros.rrImageDomain = function rrImageDomain(){
		//Round robin style
		return staticimagesurl[nextDomain++ % maxDomains];
	}

	%>

The code, combined with a few harp globals, allows you to set a dynamic image
domain for images. This allowed you to serve images from multiple domains and
specifically, leverage CDN for your site. Something I noticed after starting to
do this, is that a speed calculator, such as [GTmetrix] will give you warnings
about serving the same content from different URLs.

First, let's talk about why this matters:

When it comes to making your site fast, minimizing the number of times the browser
needs to go back to the server for any resource is important. If your site is 
image heavy, than you want to make sure	that you have proper image caching. So that
whenever your browser requests `http://example.com/images/nice.jpg`, you only ask
for it once, and then the browser caches the image and doesn't have to do anymore
work.

Now what happens if you've got the same image at: `http://example.com/images/nice.jpg`
and `http://cdn.example.com/images/nice.jpg`

Let's make an example page and try it out. Throw this HTML into a file, save it, 
and then open it:

	&lt;html&gt;
		&lt;head&gt;&lt;title&gt;My Test&lt;/title&gt;&lt;/head&gt;
		&lt;body&gt;
			&lt;img src=&quot;http://static1.ethanjoachimeldridge.info/ethan.jpeg&quot;&gt;
			&lt;img src=&quot;http://static2.ethanjoachimeldridge.info/ethan.jpeg&quot;&gt;
			&lt;img src=&quot;http://www.ethanjoachimeldridge.info/images/ethan.jpeg&quot; &gt;
		&lt;/body&gt;
	&lt;/html&gt;

And now open `about:cache` (or chrome://cache if you're on chrome) and you'll see something
like this:

<img src="/images/tech-blog/aboutcache.png" width="362px" height="134px" /> 

Clicking on one of them will give you bunches of useful information about the server
headers and the content of the image itself. Obviously, besides the domain and maybe
some headers, all of this is the same. Now why is this bad exactly? Because the
browser cache is only _so_ big. And if you're filling it with lots of big images
that are really the same, then you're losing out on the ability to cache other
images.

So how do we solve that problem if you're using my Macro? Like this:

	macros.imgSrc = function imgSrc(filePath){
		if(filePath in imagecache){
			return imagecache[filePath]
		}
		/* Take the file path and add it to the domain for the image, cache and return */
		var domain = macros.rrImageDomain()
		var src = domain + filePath
		imagecache[filePath] = src
		return src
	}
	%>

And call it like so:

	<%= macros.imgSrc("/images/nice.jpg") %>

This allows Harp to have a sort of object cache for every image you're asking it
to make. And we key the cache by the image path. So long as the image path is the
same, then we'll always get the same domain out. It's a pretty handy macro to have
and I hope it helps someone out there!

[wrote a blog post on using a CDN and Harp together]:http://www.ethanjoachimeldridge.info/tech-blog/harpjs-macros
[GTmetrix]:http://gtmetrix.com/