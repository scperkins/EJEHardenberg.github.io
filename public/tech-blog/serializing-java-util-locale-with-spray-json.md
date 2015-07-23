### Serializing java.util.Locale with spray-json

When dealing with internationalized content, a common pattern is to store 
textual information in seperate tables from the parent object. This text 
has a primary composite key of (id, lang). For example, in scala:

	case class BlogPost(id: Int, createdTimeEpoch: Long, published: Boolean)

	case class BlogPostText(blogId: Int, lang: java.util.Locale, postText: String)

And this will work just fine, as when you need to get a spanish, french, or 
english copy of your blog post you can just use a SQL `JOIN` statement and 
specify whichever language you need. Easy right? Right. What about when you're 
dealing with your data and need to serialize it over the wire? For example, 
let's say your blogPosts are sent out in some form of JSON feed that is 
consumed by an app for your site? 

There are a lot of serialization libraries, but one that caught my eye 
recently is [Spray-json]. A useful and handy library that is quite easy 
to use when it comes to standard types or case classes. The one place it 
does tend to hiccup on is when dealing with enumerations and classes which 
aren't `case`. Enumerations are easy to deal with. They can be handled 
like so:

	/** SprayJSON reader/writer for enumerated types
	 * @see https://groups.google.com/forum/#!topic/spray-user/RkIwRIXzDDc 
	 */
	def jsonEnum[T <: Enumeration](enu: T) = new JsonFormat[T#Value] {
		def write(obj: T#Value) = JsString(obj.toString)

		def read(json: JsValue) = json match {
			case JsString(txt) => enu.withName(txt)
			case something => throw new DeserializationException(s"Expected a value from enum $enu instead of $something")
		}
	}

	implicit val enumConversion =jsonEnum(YourEnumeratedTypeHere)

As referenced in the code, the above code is [courtesy of a David Perez]. However 
this is not going to help you in the case of the [Locale] class. So how do you 
do it? The defaults do not provide a formatter for this and if you attempt to 
serialize an object like `BlogPostText` above, you'll run into the error:

	could not find implicit value for evidence parameter of type spray.json.DefaultJsonProtocol.JF[java.util.Locale]

It's pretty simple to get around this though:

	implicit object LocaleFormat extends JsonFormat[java.util.Locale] {
		def write(obj: java.util.Locale) = JsString(obj.toString)
		def read(json: JsValue) : java.util.Locale = json match {
			case JsString(langString) => new java.util.Locale(langString)
			case _ => deserializationError("Locale Language String Expected")
		}
	}

The above code provides an implicit object to serialize and deserialize Locale 
objects based on the [language constructor]. We implement `JsonFormat` instead of 
the `RootJsonFormat` trait because we're not expecting to use Locale's as root 
objects in JSON trees. If your use case is otherwise you would simply switch out 
`JsonFormat` for `RootJsonFormat`.  For more detail on the difference [read here].

But this isn't the only way. An implicit object is fine, but we can also make due 
with a class:

	class JsonLocaleFormatClass extends JsonFormat[java.util.Locale] {
		def write(obj: java.util.Locale) = JsString(obj.toString)
		def read(json: JsValue) : java.util.Locale = json match {
			case JsString(langString) => new java.util.Locale(langString)
			case _ => deserializationError("Locale Language String Expected")
		}
	}

Then use it like so:

	import spray.json._
	import DefaultJsonProtocol._

	implicit val formatter = new JsonLocaleFormatClass()
		

	case class BlogPostText(blogId: Int, lang: java.util.Locale, postText: String)

	val blogpostgerman = BlogPostText(0, new java.util.Locale("de"), "Ich kann nicht versteht!")

	blogpostgerman.toJson // {"blogId":0,"lang":"de","postText":"Ich kann nicht versteht!"}

	"""{"blogId":0,"lang":"de","postText":"Ich kann nicht versteht!"}""".parseJson.convertTo[BlogPostText] // BlogPostText(0,de,Ich kann nicht versteht!)

Whether you choose to use a class and explicitly define a converter for your 
usage, or you create an implicit object to import, you can now handle Locale 
classes in your code! 

[You can find an example project to run yourself here showing the above code in use]



[Spray-json]:https://github.com/spray/spray-json
[courtesy of a David Perez]:https://groups.google.com/forum/#!topic/spray-user/RkIwRIXzDDc 
[Locale]:https://docs.oracle.com/javase/7/docs/api/java/util/Locale.html
[language constructor]:https://docs.oracle.com/javase/7/docs/api/java/util/Locale.html#Locale(java.lang.String)
[read here]:https://github.com/spray/spray-json#jsonformat-vs-rootjsonformat
[You can find an example project to run yourself here showing the above code in use]:https://github.com/EdgeCaseBerg/spray-json-locale-example

 