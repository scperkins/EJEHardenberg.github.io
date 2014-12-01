###Auto loading resource files in Harp

**An example Harp site using this technique can be found [here]**

In my [previous post] I talked about loading javascript based on filenames or the
current path + filename. But today I was thinking to myself, why stop there? After
all, a bigger concern than javascript when you're trying to have a fast rendering
website is CSS (because it's render blocking). So we always want our CSS files to
be small, bite sized, and parsable. 

That's why you always see minimizers everywhere, people advocating for putting critical
CSS in the head of the document, and etc etc. And these are all good, but we're 
compiling a static site. So why don't we just cut right to the chase and only 
include what we need?

Now I'm not saying do away with your primary styling file, not at all. A site should 
have a consistent theme, and that theme should be present within a master stylesheet.
_However_, it's often the case that you need one or two styles that only really apply
to a single page. You can put those inline perhaps, but then we lose the ability to
use [Harp]'s preprocessors like LESS. 

So I give you this slightly adapted partial from my previous post. All you have to 
do is set the javascript and the CSS path. (In some globals or passed to the partial,
either would work). And then you'll have CSS and Javascript automatically for one-off
styles and scripts.


__autoload.ejs_

	<% 
	/* Auto Script for Javascript and CSS, loads a CSS/js file into the application
	 * if the current file name and path match a file and path within a js or CSS
	 * directory
	 */
	function findResource(head, tail, filter) {
		var result = false
		for (key in head) { 
			val = head[key]
			if (key == '_contents') { 
				for (i in val) { 
					file = val[i]
					if (filter.test(tail + file) ) { 
						return true
					}
				}
			} else { 
				result = findResource(val, tail + key + "/", filter)
				if(result) return result
			}
		}
	}

		
	function resourceExists(base, ext){
		filter = new RegExp("(^/" + base + "/" + current.path.join("/")  + "\." + ext + "$)") 	
		return findResource(public, "/", filter) 
	}


	if( resourceExists(cssBase,"CSS") ){
		%><link rel="stylesheet" type="text/CSS" href="/<%= cssBase + "/" + current.path.join("/") + ".CSS" %>"><%
	}
	if( resourceExists(javascriptBase,"js") ){
		%><script type="text/javascript" src="/<%= javascriptBase + "/" + current.path.join("/") + ".js" %>"></script><%
	}	
	%>

The code works in the same way that the [XML Sitemap] does, it traverses the tree
structure of the `public` variable and tests each file against a regular expression.
It's crazy how much use you can get out of this simple technique. Sitemaps, dynamic
inclusion, analytics (an upcoming post perhaps), you can get it all just by recycling, 
all you have to do is throw this in a partial called `_autoload.ejs` and include it 
like so:

in Jade:

    != partial("_autoload")

or EJS:

    <%- partial("_autoload") %>

**An example Harp site using this technique can be found [here]**

[previous post]:http://www.ethanjoachimeldridge.info/tech-blog/dynamically-including-js
[Harp]:http://www.harpjs.com
[here]:https://github.com/EdgeCaseBerg/harp-autoload
[XML Sitemap]:http://www.ethanjoachimeldridge.info/tech-blog/xml-sitemap-for-harpjs