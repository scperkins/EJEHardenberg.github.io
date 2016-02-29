This is my website, there are many like it, but this one is mine. And
you can [view it here]

Setup:
------------------------------------------------------------------------

 - Install Harp
 - Run harp server
 - Browse to localhost:9000

Or you could just [visit the site] to see the content. 

This site uses [Harp] and is a decent example (I think) of a couple of
good macros you can use in your own. For example:

- [CDN Recipe]: use a static host and this macro to get cookieless
  images and resources onto your website, from different hosts or
  multiple, it's possible.

- [XML Sitemap]: an adaption of Harp's sitemap recipe (ordered list)
  into a search engine compliant xml format.

- [Javascript Inclusion]: a recipe on including javascript files based on your
  file path.

- [Autoload Resources]: a recipe on including both CSS and Javascript based on
  the current file path.

I also blog about my projects that I do, you can checkout the project page on 
the website for that. One of the ones that I like is my [chat server tutorial] 
series. I've also recently got into [Play!], Feel free to check it out!



[SubResource Integrity]
------------------------------------------------------------------------

SubResource Integrity (SRI) is a method to ensure that the files that an
application downloads are the correct ones. This ensures that
Compromised CDN's cannot deliver malicious code to your website. 

To setup:

	pip install beautifulsoup4
	vi sri.conf #edit as neccesary 

To run: 

	python sri.py

The python script will look for the configured files (see sri.conf) and
attempt to update the source code to have the correct hashes. Note that 
I wrote a [post about this] but don't run SRI on my site because there's 
no point since my site is served over regular HTTP.



[CDN Recipe]:http://www.ethanjoachimeldridge.info/tech-blog/harp-macro-revisit
[XML Sitemap]:http://www.ethanjoachimeldridge.info/tech-blog/xml-sitemap-for-harpjs
[Javascript Inclusion]:http://www.ethanjoachimeldridge.info/tech-blog/dynamically-including-js
[Autoload Resources]:http://www.ethanjoachimeldridge.info/tech-blog/autoload-harp-css-js
[Play!]:http://www.ethanjoachimeldridge.info/tech-blog/xml-playframework-templates
[chat server tutorial]:http://www.ethanjoachimeldridge.info/tech-blog/cgi-c-harp-1
[opinion]:http://www.ethanjoachimeldridge.info/writing/political/
[view it here]:http://www.ethanjoachimeldridge.info
[visit the site]:http://www.ethanjoachimeldridge.info
[Harp]:http://www.harpjs.com
[SubResource Integrity]:https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
[post about this]:http://www.ethanjoachimeldridge.info/tech-blog/implementing-subresource-integrity-sri
