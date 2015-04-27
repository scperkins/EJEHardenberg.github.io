### Value Raw is not a member of String (weird error in scala)

Today I was working on a pretty simple system, it involved using the 
routes of a [PlayFramework] application to decide the format of the view. 
Specifically, visiting a resource with a url ending in `.html` would 
result in an HTML page being rendered, and similarly with XML.

In addition to the type of data being display, the way it was displayed, 
or its template, also could change according to a url. For example, 
displaying a mobile view vs a desktop view, a table vs a list view, a 
view without any images or style, one with bootstrap... (you get the 
picture). 

But while writing up some error handling code I ran into a really odd 
error message:

"value raw is not a member of a String"

	[error] /path/app/views/common/templateNotFound.scala.xml:4: value raw is not a member of String
	[error] 	<Message>The template or the format does exist</Message>
	[error] 	                      ^
	[error] one error found
	[error] (compile:compile) Compilation failed

The offending code was this rather innocuous view:

	@(template: String, format: String) 
	<?xml version="1.0" encoding="utf-8"?>
	<ViewError>
		<Message>The template or the format does exist</Message>
		<Template>@template</Template>
		<Format>@format</Format>
	</ViewError>

Nothing about this code immediately jumped out to me as horribly 
incorrect, and I confused myself some more by removing parts, 
seeing the same error message, placing them back in, changing the 
file name, turning sbt on and off. And in general, scratching my head. 

After about 5 or so minutes of this, I became suspicious of my variable 
names. Having read the book [Scala Puzzlers], I knew that sometimes the 
compiler can do _some really funny stuff_. Since my view is essentially 
one giant XML literal, I guessed that maybe something was being 
interpolated or resolved in an odd way. I made the slight change: 


	@(badTemplate: String, badFormat: String) 
	<?xml version="1.0" encoding="utf-8"?>
	<ViewError>
		<Message>The template or the format does exist</Message>
		<Template>@badTemplate</Template>
		<Format>@badFormat</Format>
	</ViewError>

Saved the file and let `sbt ~compile` catch it and sure enough:

	[info] Compiling 1 Scala source to /path/target/scala-2.10/classes...
	[success] Total time: 14 s, completed Apr 27, 2015 11:45:50 PM

Hope this helps someone out there!

[Scala Puzzlers]:http://scalapuzzlers.com/
[PlayFramework]:https://www.playframework.com/documentation/2.3.x/Home