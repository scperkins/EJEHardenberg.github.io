### Implementing Subresource Integrity

A little while ago a blog post by [Frederik Braun] came across my radar
and I learned about something call [Subresource integrity]. You can read
the excellent explanation by Braun [on his website] for more details or
you can [read his transcript] of a talk he gave if you want a really
thorough explanation of how it works, what it is, and why it's useful.
For this blog post, I'm focused on the practical people who simply want
to _use_ SRI and advise a few things to be mindful of as you implement. 

#### For those who don't want to read, what's SRI?

SRI is a way to make sure CDN or other third party assets such as
javascript or CSS don't deface your site or do malicious things should 
said third party become compromised. You can imagine a situation where
you include jQuery from [cdnjs], but it's been compromised, so every few
seconds it does a simple call to load facebook silently.
Congratulations, the world has just DDoS-ed a website for you _and you
could have prevented it with SRI_. 

#### Getting to it, the key parts for SRI. 

To implement SRI for your resource you need 2 things. 

1. The hash of your resource, using sha256, sha384, or sha512\*
2. The Base 64 encoding of your hash.

You can compute this yourself with open SSL as Braun indicates on his
website

	cat MYFILE | openssl dgst -sha256 -binary | openssl enc -base64 -A

or you can use [this handy website to generate the HTML for a given file].

If you're only doing this for a few resources on your pages (jQuery,
bootstrap, etc) then you're probably fine using one of these tools and
adding in the HTML manually. If you're like me, and like to automate
things then you can do a bit more work. 

#### Automating SRI for your website, via Python

If you just want the script, [it's here] and you'll just need to
[configure it]. 

If I were any good with Node or understanding the finer nature of [Harp]
I'd be able to integrate the integrity checks directly into the compile
step of my website, but since I don't know how to do that I figure'd
python would be a safe alternative. I chose python because it provides:

- An easy to use HTML parser via [Beautiful Soup]
- An easy to use hashing library via [Hashlib]
- And an encoding library for [Base64] and [JSON]

The gist of the script is simple, using a configuration for which files
should have integrity checks added to them, walk an HTML folder and
update each of the links with the appropriate intregity value. So, we
need to:

1. Load a configuration
2. Compute integrity values for the configured files
3. Walk and update each HTML file.

#### Loading a configuration

In python, loading a simple JSON configuration file couldn't be simpler:

	import json
	with open('sri.conf') as f:
		conf = json.load(f)

We'll be provided with a simple dictionary to use of whatever happens to
be in _sri.conf_. In my case it's:

	{
		"scripts" : [
			["www/javascript/app.js", "/app.js"],
			["www/javascript/jquery.min.1.9.1.js", "/jquery.min.1.9.1.js"]
		],
		"links" : [
			["www/css/style.css", "/style.css"],
			["www/css/non-essentials.css", "/non-essentials.css"],
			["www/css/politics.css", "/politics.css"]
		]
	}

The configuration is simple, I'll be handling both javascript `script`
tags and CSS `link` tags. The items in the array are arrays of length 
2, with the first element being the resource to validate, and the second
being the script to look for. Since my website [chooses one of my static hosts randomly] 
I don't know the full domain to search for and simply look for a match
at the _end_ of a file, which means that if there were more than one
app.js, this script would have some issues. Caveat aside, it's trivial 
to move on to the next step. 

#### Computing integrity values for SRI in Python

It's simple to call `hashlib.sha384()` and `update` on a set of bytes to
compute a hash in python:

	import hashlib
    sha = hashlib.sha384()
	sha.update("block")
	print sha.hexdigest()

But what's not entirely clear is whether you should use `hexdigest` or
`digest`. If we _only_ needed the sha value and not the base 64 encoded
version as well, we'd probably prefer `hexdigest` since, according to
the docs:

>the digest is returned as a string of double length, containing only
>hexadecimal digits. This may be used to exchange the value safely in
>email or other non-binary environments.

But since we'll be passing it to `base64.encodestring`, we want to use
`digest` which has a return value that is the raw hash and not a string
encoding of it that would hash differently:

>This is a string of digest\_size bytes which may contain non-ASCII
>characters, including null bytes.

We're using the `base64.encodestring` method rather than `b64encode` or
any of the other methods because, according to the [Base64] docs:

>The legacy interface provides for encoding and decoding to and from
>file-like objects as well as strings, but only using the Base64
>standard alphabet.

The community for python is great, so I didn't have to expend too much
effort in finding [an example of hashing a file], and my only update was
to use `digest` rather than `hexdigest` so I didn't have to convert from
the hex version back to the raw for my base64 encoding.


	import hashlib
	def sha384OfFile(filepath):
	    sha = hashlib.sha384()
	    with open(filepath, 'rb') as f:
	        while True:
	            block = f.read(2**10) # Magic number: one-megabyte blocks.
	            if not block: break
	            sha.update(block)
	        return sha.digest()

And to compute the base64 encoding and format the string into a valid
integrity check for SRI:

	def sriOfFile(filepath):
		sha = sha384OfFile(filepath)
		return 'sha384-' + encodestring(sha)[:-1] #drop newline added by b64

Note that we have to drop the last line because `encodestring` adds a
newline as indicated by the documentation:

>returns a string containing one or more lines of base64-encoded data
>always including an extra trailing newline ('\n').

#### Walking HTML files and adding SRI

Finally, the last thing we need to do is traverse a file system and open
and edit each HTML file. Walking directory structures is fairly trivial
in Python:

	directory = '/tmp'
	for root, directories, files in os.walk(directory):
        for filename in files:
			#Do stuff

To only deal with HTML files we simply check the filename:

	if filename.endsWith(".html"):
		#Do stuff

So combining these two together we can construct a list of files that we
need to update and edit:

	def get_filepaths(directory):
	    file_paths = []  # List which will store all of the full filepaths.
	
	    for root, directories, files in os.walk(directory):
	        for filename in files:
	            if filename.endsWith(".html"):
		            filepath = os.path.join(root, filename)
		            file_paths.append(filepath)  # Add it to the list.

	    return file_paths  # Self-explanatory.

Once we have the files, we parse them with [BeautifulSoup] and update
the `link` and `script` tags with the configured values if they match
our search pattern. Parsing a file is easy:

	# f being a member of the get_filepaths return array
	with open(f,'r') as openedFile:
			soup = BeautifulSoup(openedFile, "lxml")

Then, finding valid links to update can be done with the `find_all`
method on the `soup` by providing our own filtering functions:

	def isCssLink(tag):
		return tag.has_attr('rel') and tag.has_attr('href') and 'stylesheet' in tag['rel']
	
	def isScriptLink(tag):
		return tag.has_attr('src') and tag.has_attr('type') and 'text/javascript' in tag['type']

	links = soup.find_all(isCssLink)
	scripts = soup.find_all(isScriptLink)

Once we have all the CSS links and javascript script tags, we can update
them with soup's easy to understand syntax:

	for link in links:
		link['property'] = 'value'

So going back to our configuration JSON, we know we have a pattern to
search, and a file to hash. Pre-computing these will save us a lot of
time and effort performance wise:

	searchLinks = []
	searchScripts = []
	
	for linkArray in conf['links']:
		sri = sriOfFile(linkArray[0]) #linkArray[0] is the filepath
		searchLinks.append( [linkArray[1] , sri]) #linkArray[1] is the pattern to search
	
	for scriptArray in conf['scripts']:
		sri = sriOfFile(scriptArray[0])
		searchScripts.append( [scriptArray[1] , sri])

With these pre-computed SRI's and patterns we can update our HTML soup:

	for link in links:
		for searchLink in searchLinks:
			if link['href'].endswith(searchLink[0]):
				link['integrity'] = searchLink[1]
				link['crossorigin'] = 'anonymous'

And just like that we have an updated HTML file, and all that's left is
to save it:

	data = soup.prettify()

	with open(f, 'w') as openedFile:
		openedFile.write(data.encode('utf-8'))

#### Things to note

With the script explained, there are a few things I'd like to make note
of. While updating my own site to use SRI I [managed to break it for a while]. 
Namely because I _forgot to add the crossorigin attribute_ to the tag.
You **absolutely** need to include it, otherwise the asset will not
load. And depending on your browser version, you might not get a clear
[message about it in the error console]. But the main thing you need to
remember is to add the crossorigin attribute. And of course, add CORS
headers to whatever is serving the assets, most CDN do already.

The other thing to note is that your integrity value doesn't actually
ensure anything unless it's in a secure context, i.e. if the asset is
loaded via SSL. While the SRI spec _has no requirement for SSL_ on the
loaded source, it still advises developers that they're just wasting
people's time if it's not:

>Being in a Secure Context (e.g., a document delivered over HTTPS) is
>not necessary for the use of integrity validation. Because resource
>integrity is only an application level security tool, and it does not
>change the security state of the user agent, a Secure Context is
>unnecessary. However, if integrity is used in something other than a
>Secure Context (e.g., a document delivered over HTTP), authors should
>be aware that the integrity provides no security guarantees at all. For
>this reason, authors should only deliver integrity metadata in a Secure
>Context. See [Non-secure contexts remain non-secure] for more discussion.

And finally, SRI is still experimental and is supported by chrome and
firefox in their latest/nightly versions. If you want to see if your
browser is supported, you can open the [srihash.org page] and scroll to
the bottom.

Stay secure and I hope this helps!

\*<small>The list of supported hash algorithms is in [S 3.5 of the SRI spec], which in
turn references [Content Security Policy Level 2, section 4.2].<small>



[Frederik Braun]:https://frederik-braun.com/index.html
[Subresource integrity]:http://www.w3.org/TR/SRI/
[on his website]:https://frederik-braun.com/subresource-integrity.html
[read his transcript]:https://frederik-braun.com/using-subresource-integrity.html
[cdnjs]:https://cdnjs.com/
[S 3.5 of the SRI spec]:https://w3c.github.io/webappsec-subresource-integrity/#the-integrity-attribute
[Content Security Policy Level 2, section 4.2]:http://www.w3.org/TR/CSP11/#source-list-syntax
[this handy website to generate the HTML for a given file]:https://www.srihash.org/
[it's here]:https://github.com/EdgeCaseBerg/EJEHardenberg.github.io/blob/master/sri.py
[configure it]:https://github.com/EdgeCaseBerg/EJEHardenberg.github.io/blob/master/sri.conf
[managed to break it for a while]:https://github.com/EdgeCaseBerg/EJEHardenberg.github.io/issues/2
[Harp]:http://www.harpjs.com/
[BeautifulSoup]:http://www.crummy.com/software/BeautifulSoup/
[Hashlib]:https://docs.python.org/2/library/hashlib.html
[Base64]:https://docs.python.org/2/library/base64.html#module-base64
[JSON]:https://docs.python.org/2/library/json.html
[chooses one of my static hosts randomly]:/tech-blog/harpjs-macros
[an example of hashing a file]:http://stackoverflow.com/a/19711609/1808164
[message about it in the error console]:https://code.google.com/p/chromium/issues/detail?id=527436
[Non-section contexts remain non-secure]:http://www.w3.org/TR/SRI/#non-secure-contexts-remain-non-secure
[srihash.org page]:https://www.srihash.org/
