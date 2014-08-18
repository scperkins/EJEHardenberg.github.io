###Generating an XML Sitemap For HarpJS

So, quite frankly, I really enjoy using [Harp] to manage my website. I love 
markdown, I love simple and easy conventions for site compilation. Heck, I
think the file.datatype.ejs is extremely clever and very useful. Here's one
of the reasons why:

**Generating an XML Sitemap with Harp of your entire site is really easy.**

Harp's site [has a recipe for a Sitemap], however this generates an HTML ordered
list. While this functions for your users as a map, it's not the easiest format
for a googlebot to crawl. That would be the [Sitemap Protocol]. Which is simply
a list of links (plain txt) or an XML document. 

It's straightfoward to generate a list of links using harp's recipe, but let's
go ahead and generate the XML version of a sitemap. I'll use my website as an
example.

Here's the code:

	<?xml version="1.0" encoding="UTF-8"?>
		<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><%
	var filter = /(\.html$)/; 
	var replace = /(\.html$)|(^index\.html$)/; 

	function tree(head, tail) {
	  	for (key in head) { 
	    	val = head[key]; 
	    	if (key !== '.git' && key !== '_data') { 
		      	if (key == '_contents') { 
			        for (i in val) { 
			          	file = val[i]
			          	if (filter.test(file) && !/^404\.html/.test(file)) { 
			            	file = file.replace(replace, ""); 
			            	date = null
			            	freq = "daily"
			            	if(head['_data']){
			                   	obj = head['_data'][file]
			                   	if(obj && obj.date){
			                   		date = new Date(Date.parse(obj.date)).toISOString()
			                   	}
			                   	if(obj && obj.freq){
			                   		freq = obj.freq
			                   	}
			                }
			                if(!date){
			                	date = new Date().toISOString()
			                }
	%><url>
		<loc>http://wwww.ethanjoachimeldridge.info<%= tail + file %></loc>
		<changefreq><%= freq %></changefreq>
		<lastmod><%= date %></lastmod>
	</url>
	<%
			           }
			        }
		      	} else { 
		        	tree(val, tail + key + "/")
				}
	    	}
		}
	}

	tree(public, "/") 
	%></urlset> 

If you've looked at Harp's recipe you'll notice that the tree function is nearly
word for word the same. That's because I adapted Harp's recipe for my own. What
changed? 

1. We're wrapping the whole list in the XML version and schema tags
2. We're telling search engines how often our content changes [daily, monthly...]
3. And we're also telling them when the file changed last (sort of)

Something that I'm not doing here is actually [stat]ing the files to see when they
were last modified. If I figure out how to do this from Harp's environment I'll update
this post. But my way simply uses the last compilation date of your website if you
don't set any date meta field in your file's meta data.

What I mean by that last bit, if it's not clear, is that in my `_data.json` file
for my blog directories, I have a meta field called 'date' where I have already 
entered a date (in the format of YYYY-MM-DD if you're wondering), the code simply
parses that date and converts it into ISO format. Nothing hard.

If you use this recipe, you'll need to change the `<loc>` tag to have _your_ domain
name on it. Sitemap URL's should **always** be absolute. So be sure to do go ahead
and do that so you don't spam my server with 404's ;)	

**Update: August 18th, 2014**

We can set the `freq` tag for the XML to whatever we want from the metadata for
any page by specifying: `"freq" : "<freq>"`, simply replace `<freq>` with [daily, monthly...]

[Harp]:http://harpjs.com
[has a recipe for a Sitemap]:/http://harpjs.com/recipes/blog-sitemap
[Sitemap Protocol]:http://www.sitemaps.org/protocol.html
[daily, monthly...]:http://www.sitemaps.org/protocol.html#changefreqdef
[stat]:http://linux.die.net/man/1/stat