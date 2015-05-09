### Dot Paths in Harp 0.17.0 -- a Bug? 

Today when I was writing [my last post] I ran into a funny bug with the 
way that [Harp] handles url paths. Namely, I wanted my url path for the 
post to be: _"value-enablePlugins-is-not-a-member-of-sbt.Project"_ in 
order to capture the error message properly. But when I did this I got 
an error form harp! Complaints about not finding the value for the key 
in my __data.json_ file. 

Investigating,  `console.log(current.source)` told me that the expected 
source key was: _"value-enablePlugins-is-not-a-member-of-sbt"_. Clearly 
missing the last piece, and thus causing 

	<% if ( ! public["tech-blog"]._data[current.source].draft) { %><%- yield %>

in my layout file to err. I [isolated the error] and created a simple 
file that had a bunch of dots in its name. Then logged the source field 
from the layout file:

<img src="/images/tech-blog/harpdotbug.jpg">

If I typed in the file extension the file would download instantly instead 
of showing in the browser. This happened when it was hitting either of 
these urls:

- http://localhost:9000/a.key.with.dots.html
- http://localhost:9000/a.key.with.dots

And the log which you can see in the screenshot showed that the key for 
the file, was simple `a` instead of `a.key.with.dots` as expected.

If I go to http://localhost:9000/a.key.with.dots.md I simply get a 404 
page. 

Assuming that I was wrong about what I thought urls could be, I checked 
out [RFC 1738] and looked into restrictions on the path. Section 3.3 
defines the HTTP standards and all it had to say on the matter was:

>Within the <path> and <searchpart> components, "/", ";", "?" are
>reserved.  The "/" character may be used within HTTP to designate a
>hierarchical structure.

The grammar is defined as:

	urlpath        = *xchar    ; depends on protocol see section 3.1

And looking up what the `xchar` is defined as results in:

	xchar          = unreserved | reserved | escape
	reserved       = ";" | "/" | "?" | ":" | "@" | "&" | "="
	escape         = "%" hex hex
	unreserved     = alpha | digit | safe | extra
	safe           = "$" | "-" | "_" | "." | "+"

No restrictions on dots there, in fact, since they're part of the `safe` 
set, they're allowed in the urls (obviously since we can do things like 
.html). Reading through the RFC I didn't find anything specifically saying 
that the dot had to specify an extension only, so I can only conclude 
that urls like: "a.url.with.dots" are allowed. 

Under this assumption, [Harp] is not respecting the RFC, and specifically 
it is stripping the key from the JSON file to the first part before _any_ 
dots. For now, until this is fixed you'll need to avoid using dots in URLs.

[Harp]:http://harpjs.com
[my last post]:/tech-blog/value-enablePlugins-is-not-a-member-of-sbt-Project
[isolated the error]:https://github.com/EdgeCaseBerg/harp-keys-with-dots-bug-example
[RFC 1738]:https://www.ietf.org/rfc/rfc1738.txt