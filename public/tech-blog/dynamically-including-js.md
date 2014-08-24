###Dynamic Javascript Inclusion Recipe for Harp

Today I was thinking about how great it would be to include only the javascript 
files you need on a webpage, and how best to break it up. If you have global library 
files like [jQuery] it makes sense to have them on every page. But what if you 
have a single use case for some javascript? 

Here's my use case:

You want to show a popup on your main page, and are tired of doing checks like this:

    var flag = document.getElementById("someflagelement")
    if(flag){
    	alert("POP UP!")
    }

It's not a big problem to do, but now your javascript is tied to the existence of 
certain tags on your page, it's undocumented and if someone accidently names their
element the same then a pop up is going to appear. Not good. Another scenario is
when you have a **large** site and you don't want to have one giant javascript 
file that you include on every page. For that problem I offer the following Harp 
recipe:

	var src = current.source
	var filter = new RegExp("("+src+"\.js$)"); 

	function findDynamicJavaScript(head, tail) {
  		for (key in head) { 
    		val = head[key]; 
      		if (key == '_contents') { 
	        	for (i in val) { 
	          		file = val[i]
	          		if (filter.test(file) ) { 
	            	%><script type="text/javascript" src="<%= tail + file %>"></script><%
	            	}
	        	}
      		} else { 
        		findDynamicJavaScript(val, tail + key + "/")
			}
		}
	}

	findDynamicJavaScript(public, "/") 

So what does this do? This function is very similar to the [Sitemap] recipe from 
Harp (or to [my XML Sitemap] recipe) in that it traverses the directories harp knows
about and uses a RegEx to check whether the file matches a pattern or not. In this 
case, we use the current source as our query. This means that on _index.html_, if a
javascript file named _index.js_ exists, it will be pulled onto the page. 

**Note**: <small>The regular expression above would also detect /otherindex.js as well 
since the expression doesn't check the path at all.</small>

This is rather useful since it keeps your file structure semantically aligned. For 
someone coming to your codebase, if they see something happening on a page and want
to know where it's coming from, they'll immediately spot the javascript file with 
the same name when they look in your scripts directory. This is a **great** thing
when you're working with other people.

But what if we have multiple index files? After all, there's one per directory typically.

In that case we should be testing the full path. So we can modify our recipe like so:

	var src = current.path.join("/")
	var javascriptBase = "/js/"
	var filter = new RegExp("(^"+javascriptBase+src+"\.js$)"); 

	function findDynamicJavaScript(head, tail) {
	  	for (key in head) { 
	    	val = head[key]; 
	      	if (key == '_contents') { 
		        for (i in val) { 
		          	file = val[i]
		          	if (filter.test(tail + file) ) { 
		            	%>
		            	<script type="text/javascript" src="<%= tail + file %>"></script>
		            	<%
		            }
		        }
	      	} else { 
	        	findDynamicJavaScript(val, tail + key + "/")
			}
		}
	}

	findDynamicJavaScript(public, "/") 

All we're doing is using the current path (joined by "/") to look more specifically
at the files we're testing. We need to have `javascriptBase` because we're looking
for javascript files that match the path to our html files. 

This is a simple and easy recipe to handle including javascript based on the current
file being served. It keeps your code clean, consistent, and developer friendly.
I hope it helps someone out there!

[jQuery]:http://www.jquery.com
[Sitemap]:http://harpjs.com/recipes/blog-sitemap
[my XML Sitemap]:http://www.ethanjoachimeldridge.info/tech-blog/xml-sitemap-for-harpjs