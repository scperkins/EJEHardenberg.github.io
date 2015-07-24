### Serializing JSON and Generic Classes with spray-json

Continuing on from where [the last post] left off, let's talk about structure. 
Whether or not you're working in an object oriented paradigm or a functional 
one, having base classes and a nice class hierarchy can make your code easier
to understand and use. Of course since we'll be working in example code, none 
of these classes will _actually_ be useful, but hey, you can always apply the 
concepts yourself.

So let's say you've got a base class and a couple of subclasses: 

	class Base(msg: String)

	case class Thing1(msg: String, thing1Thing: String) extends Base(msg)

	case class Thing2(msg: String, thing2Thing: String) extends Base(msg)

It's easy to define a few conversion implicits:

	
	import spray.json._
	import spray.json.DefaultJsonProtocol._
	implicit val thing1Conversion = jsonFormat2(Thing1)
	implicit val thing2Conversion = jsonFormat2(Thing2)
ning
And we can use the `toJson` and `convertTo[ClassName]` methods from the spray
package just fine. But what about when we want to do something like this:

	case class ServiceResponse(status: Int, result: Base)

And then define a serializer for that? Attempting to create one with the `jsonFormat2` 
call will fail:

	implicit val srConv = jsonFormat2(ServiceResponse)
	<console>:23: error: could not find implicit value for evidence parameter of type spray.json.DefaultJsonProtocol.JF[Base]
	
and conveniently tell you that you need to define a protocol for the `Base` class. 
Because case classes inherentance is prohibited by the compiler, we need to handle 
`Base` as we would any other normal class. So we provide `JsonFormat[T]` for it. 
The write method is simple:

	implicit object ColorJsonFormat extends RootJsonFormat[Base] {
		def write(c: Base) = c match {
			case s: Thing2 => JsObject(("msg",JsString(s.msg)), ("thing2Thing",JsString(s.thing2Thing)))
			case s: Thing1 => JsObject(("msg",JsString(s.msg)), ("thing1Thing",JsString(s.thing1Thing)))
			case _ => serializationError(s"Could not write object $c")
		}
		...

We pattern match according to the type, then proceed to construct a simple JSON 
object out of the data. What about reading?

	def read(json: JsValue) = {
		json match {
			case JsObject(map) => 
				List("msg","thing1Thing","thing2Thing").map(i => map.contains(i)).toArray match {
					case Array(true,true,false) => Thing1(map("msg").toString, map("thing1Thing").toString)
					case Array(true,false,true) => Thing2(map("msg").toString, map("thing2Thing").toString)
					case _ => deserializationError("fields invalid")
				}
			case _ => deserializationError("Base expected")
		}
	}

The above is a bit clunky since we can't [pattern match against a Map]. But you 
can now use the ServiceResponse like so:

	implicit val srConv = jsonFormat2(ServiceResponse)
	"""{"status" : 200, "result" :{"msg":"a","thing1Thing":"t"}}""".parseJson.convertTo[ServiceResponse]
	//res0: ServiceResponse = ServiceResponse(200,Thing1("a","t"))

But we can make this code a bit easier to deal with by leveraging implicit conversions 
on each of our subclasses:
	
	implicit val thing1Conversion = jsonFormat2(Thing1)
	implicit val thing2Conversion = jsonFormat2(Thing2)

	class BaseConversion extends RootJsonFormat[Base] {
		def write(obj: Base) = obj match {
			case t1: Thing1 => t1.toJson
			case t2: Thing2 => t2.toJson
			case _ => serializationError("Could not serialize $obj, no conversion found")
		}
		
		def read(json: JsValue) = {
			val discrimator = List(
				"thing1Thing", //Thing1 unique field
				"thing2Thing" //Thing2 unique field
			).map( d => json.asJsObject.fields.contains(d) )
			discrimator.indexOf(true) match {
				case 0 	=> json.convertTo[Thing1]
				case 1 	=> json.convertTo[Thing2]
				case _ => deserializationError("Base expected")
			}
		}
	}

We still need to work a bit of voodoo on the `read` function in order to discriminate 
between the two different types, but so long as we always have a unique field to 
go by, we'll be ok.




[the last post]:/tech-blog/serializing-java-util-locale-with-spray-json
[pattern match against a Map]:https://stackoverflow.com/questions/13536619/pattern-matching-against-scala-map-type

java.lang.RuntimeException: Cannot automatically determine case class field names and order for 'example.Thing1', please use the 'jsonFormat' overload with explicit field name specification
