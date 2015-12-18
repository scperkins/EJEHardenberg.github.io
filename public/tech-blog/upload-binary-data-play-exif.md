### Reading Binary Data in a Play Controller 

Today I was reading some [code from the Guardian] and ended up looking
into [Drew Noakes metadata extractor library]. Since I've written blog 
posts [about images before] and [how to manipulate them] I figure'd it 
might be fun to dive into reading Exif data. I'm not going to talk about 
_how_ to extract the data, but rather how you can use Drew Noake's library 
on the backend without having to send the entire image file across the net. 

While you can [parse the exif data with javascript], writing a library for 
that that works with images of all kinds of different formats isn't something 
I want to do. Instead, I'd rather send the data to the back and use Drew's 
[metadata extractor]. So first I need to figure out how to _get_ the part of 
the file that has exif data. According to the page 11 of the [specification:]

>The size of APP1 including all these elements shall not exceed the 64 Kbytes specified in the JPEG standard. 

Of course, according to the javascript post:

>The Exif specification states that all of the data should exist in the first 64kb, but IPTC sometimes goes beyond that, especially when formatted as XMP.

So we'll be safe and use the first 128kb of the image data. Using the 
[FileReader] object in the browser we can do this easily. 

	var input = document.getElementById('somefileinput');
	var readerForExif = new FileReader();
	readerForExif.readAsArrayBuffer(input.files[0]);
	readerForExif.result.slice(0, 1024 * 128);

Assuming you wait after calling `readAsArrayBuffer`, the you'll get back 
an [ArrayBuffer] that you can manipulate. Putting this together and using 
the `onload` field of our reader we can make a simple block of code 
that posts binary data to a server from the front end javascript:

	var readerForExif = new FileReader();
	readerForExif.onload = function (e) {
		var first128Kb = e.target.result.slice(0,1024 * 128);
		var view = new Uint8Array(first128Kb);
		var xhr = new XMLHttpRequest;
		xhr.open("POST", "/exif", true);
		xhr.send(view);
	};
	readerForExif.readAsArrayBuffer(input.files[0]);

Easy right? In a production implementation you might want to specify 
a content type header of `application/octet-stream`\*, but for this 
example the above code is enough to get you sending data to your 
backend. Once the data is posted we need to parse it. 

Play has a bunch of [BodyParsers], and unsurprisingly, for something 
as _raw_ as a byte stream, we'll be using the `raw` parser! To invoke 
the parser we simple start our controller action like so:
	
	import play.api._
	import play.api.mvc._

	class MyController extends Controller {
		def myFunc = Action(parse.raw) { implicit request => 
			val rawParser = request.body
			val maybeBytes = rawParser.asBytes() //Tada! Option[Array[Bytes]]!
			...
		}
	}

We still need one tweak to make this work with our front end code 
though. According to the [documentation] the maximum body size 
our parser will parse is 100KB unless we specify `play.http.parser.maxMemoryBuffer`
in application.conf. However, I found that this property didn't 
effect the raw parser, [probably because it's hard coded]. They've 
[fixed this in the newer play versions], but I got around this 
by specifying the maximum content length size directly in the action:

	def myFunc = Action(parse.raw(1024 * 124)) { implicit request => 

So all together the method to read binary data becomes extremely 
easy: 
	
	import play.api.libs.json._
	def readExifFromBinary = Action(parse.raw(1024 * 128)) { implicit request =>
		val raw = request.body
		val bytes = raw.asBytes().getOrElse(Array[Byte]())
		val exif : Map[String,String] = readExifFrom(bytes)
		Ok( Json.toJson(exif) )
	}

The only thing left to do is to create `readExifFrom(b: Array[Bytes])`. 
If you peak at the [javadocs for ImageMetadataReader] you'll notice that 
there is an overloaded version of `readMetadata` that takes a [BufferedInputStream].
It's trivial to convert an array of bytes to a BufferedInputStream
by using [ByteArrayInputStream]
	
	val inputStream = new java.io.ByteArrayInputStream(bytes)
	val bufferedInputStream = new java.io.BufferedInputStream(byteArrayInputStream)

And then we can create an instance of the [Metadata] class:

	val metadata = ImageMetadataReader.readMetadata(bufferedInputStream)

and then follow the the [general idea the guardian uses] to create a 
simple String to String Map.

	import scala.collection.JavaConversions._

	metadata.getDirectories().toList.flatMap { dir =>
		dir.getTags()
			.filter(_.hasTagName()).toList
			.map { tag =>
				tag.getTagName() -> Option(tag.getDescription).fold("")(identity)
			}
	}.toMap

The only interesting thing of note here is that we use `Option` to 
make sure we don't accidently get a null value for our descriptions. 
Once you have these building blocks in place, we have an extremely 
simple exif reading method that is both efficient and leverages all 
the power of the server side\*\* while taking advantage of the newer 
[javascript File API] to cut down how much data we have to send to 
the back end to get information about our file. 


\*<small>Among other things, you may want to make it cross browser too depending on your use case.</small><br/>
\*\*<small>Not to mention type safety and extensive java libraries to deal with different image format types</small>

[code from the Guardian]:https://github.com/guardian/grid/blob/master/image-loader/app/lib/imaging/FileMetadataReader.scala
[Drew Noakes metadata extractor library]:http://metadata-extractor.googlecode.com/svn/trunk/Javadoc/overview-summary.html
[about images before]:/tech-blog/aspect-ratios-and-math
[how to manipulate them]:/tech-blog/could-not-instantiate-SVGImageReader-Scrimage
[parse the exif data with javascript]:http://code.flickr.net/2012/06/01/parsing-exif-client-side-using-javascript-2/
[metadata extractor]:https://github.com/drewnoakes/metadata-extractor
[specification:]:http://www.exiv2.org/Exif2-2.PDF
[BodyParsers]:https://www.playframework.com/documentation/2.4.x/ScalaBodyParsers
[FileReader]:https://developer.mozilla.org/en-US/docs/Web/API/FileReader
[ArrayBuffer]:https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer
[documentation]:https://www.playframework.com/documentation/2.4.x/ScalaBodyParsers#Specifying-a-body-parser
[project because it's hard coded]:https://github.com/playframework/playframework/blob/2.3.x/framework/src/play/src/main/scala/play/api/mvc/ContentTypes.scala#L351
[fixed this in the newer play versions]:https://www.playframework.com/documentation/2.4.x/Migration24#Maximum-body-length
[javadocs for ImageMetadataReader]:http://metadata-extractor.googlecode.com/svn/trunk/Javadoc/com/drew/imaging/ImageMetadataReader.html
[BufferedInputStream]:https://docs.oracle.com/javase/7/docs/api/java/io/BufferedInputStream.html
[ByteArrayInputStream]:https://docs.oracle.com/javase/7/docs/api/java/io/ByteArrayInputStream.html
[Metadata]:http://metadata-extractor.googlecode.com/svn/trunk/Javadoc/com/drew/metadata/Metadata.html
[general idea the guardian uses]:https://github.com/guardian/grid/blob/master/image-loader/app/lib/imaging/FileMetadataReader.scala#L43
[javascript File API]:https://developer.mozilla.org/en-US/docs/Web/API/File
