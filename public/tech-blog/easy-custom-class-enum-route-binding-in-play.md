### Easy Custom class/enum Route & Query binding in Play! Framework

#### TL;DR;

Both PathBindable and QueryStringBindable have an inner class called 
`Parsing` which can be used to quickly define a binding as you see fit.
Use this to write your methods without having to define a `*Bindable` 
with two overridden methods yourself. 

From what I can tell you can't bind a class from a route parameter 
unless it's possible to create your class from a single parameter. This 
is because path binders only have 1 value available for the binder at a
time.

#### Quick Examples

_Note: See the details section below for some important caveats about these examples_

Bind a class in the route:

	case class TestObject(a: String, b: Int)

	object TestObject {
		/** Define String => T, T => String, (String, Exception) => String 
		 *  to handle binding, unbinding, and exception handling
		 */
		implicit object testObjectRouteBinder extends PathBindable.Parsing[TestObject](
			TestObject(_, 0/*<-- this is set by you because the route cant do both a & b*/), 
			_.a, 
			(key: String, e: Exception) => "Cannot parse %s as TestObject: %s".format(key, e.getMessage())
		)
	}

	class TestController() extends Controller {
		def testClass(param: TestObject) = Action {
			Ok(param.toString)
		}
	}

	// In route file:
	GET /test/class/:name @controller.TestController.testClass(name: controller.TestObject)

Bind an Enumeration in the route:

	object MyEnum extends Enumeration {
		type MyAlias = Value
		val foo = Value("foo")
		val bar = Value("bar")

		implicit object myEnumBinder extends PathBindable.Parsing[MyAlias](
			withName(_), _.toString, (k: String, e: Exception) => "Cannot parse %s as MyEnum: %s".format(k, e.getMessage())
		)
	}

	class TestController() extends Controller {
		def testEnum(enum: MyEnum.MyAlias) = Action {
			Ok(enum.toString)
		}
	}

	// In route file:
	GET /test/enum/:value @controller.TestController.testEnum(value: controller.MyEnum.MyAlias)

Bind a class or enumeration from query parameters can be done in the 
same way as path binding but instead of `PathBindable.Parsing` you use 
`QueryStringBindable.Parsing`. However, if you need to use more than one 
value when setting up the binding, you'll need to do a little more work 
by overriding the `bind` and `unbind` methods like the [documentation shows in the scaladoc].
Note that if your case class has a string value, bring the implicit 
string binder from play into scope like so:

	implicit def queryStringBinder(
		implicit intBinder: QueryStringBindable[Int], 
		stringBinder: QueryStringBindable[String]
	) = new QueryStringBindable[TestObject] {
		override def bind(key: String, params: Map[String, Seq[String]]): Option[Either[String, TestObject]] = {
			for {
				a <- stringBinder.bind(key + ".a", params)
				b <- intBinder.bind(key + ".b", params)
			} yield {
				(a, b) match {
					case (Right(a), Right(b)) => Right(TestObject(a, b))
					case _ => Left("Unable to bind a TestObject")
				}
			}
		}
		override def unbind(key: String, pager: TestObject): String = {
			stringBinder.unbind(key + ".a", pager.a) + "&" + intBinder.unbind(key + ".b", pager.b)
		}
	}

you'll want to use the `stringBinder` here in the `unbind` method to 
properly escape the value. You don't want to generate an invalid query 
string!

There's no rule that says you need to use the key + `.field` when binding 
parameters. For example, if you knew that some class would _always_ be 
bound with the same query parameter names you could hard code them and 
drop the `.` convention. The above binder would be used say if you had a 
route like

	GET /test/q/class @controller.TestController.testClass(thing: controller.TestObject)

And would be called correctly with a request like 

	/test/q/class?thing.a=Test%20Thing&thing.b=3

Take note that the the `key` being bound here is pulled from `thing` defined 
as the argument name in the routes file.


#### Useful note about the above path examples

Because under our path binders convert to `String` and back, the default 
binder that play's framework defines is called on our values. That means 
that we don't have to worry about encoding or decoding the values from 
the URL's path ourselves.


#### A slightly more realistic example

So you're writing a controller in play, and you decide that for some 
parameter of your query, say a sorting or ordering parameter, you want 
to use an Enumeration like this:

	object RequestedOrder extends Enumeration {
		type Order = Value

		val ascending = Value("ASC")
		val descending = Value("DSC")
	}

And to go along with this you have a number of different field's you'll 
be sorting by, which you've also enumerated:

	object SortingBy extends Enumeration {
		type Field = Value

		val id = Value("id")
		val someField = Value("someField")
		// etc ...
	}

Your system has more than one data type though, and each has slightly 
different fields, so you define a few more enumerations (maybe you'd 
define them all in one enumeration, but for the sake of this example 
let's roll with this)

	object DataType1SortableFields extends Enumeration {
		type Field = Value
		val id = Value("id")
		val someOtherField = Value("someOtherField")
		val anotherField = Value("anotherField")
	}

This goes on for a while, and then you decide that because you're a good 
person (or because you're getting tired of writing error handling code 
in the controller for transforming raw `String`s to your `Enumeration` 
types) you'll use the enumeration type in your routes/controller 
signatures. This is all well and dandy so you then define query/route 
binders for each of your enumerations:

	implicit object testObjectRouteBinder extends PathBindable.Parsing[RequestedOrder](
		RequestedOrder.withName(_), _.String, (k: String, e: Exception) => "Cannot parse %s as RequestedOrder: %s".format(k, e.getMessage())
	)
	implicit object testObjectQueryBinder extends QueryStringBindable.Parsing[RequestedOrder](
		RequestedOrder.withName(_), _.String, (k: String, e: Exception) => "Cannot parse %s as RequestedOrder: %s".format(k, e.getMessage())
	)
	... repeat for SortingBy and DataType1SortableFields

Seems like we've still got a lot of boiler plate doesn't it? For each of 
our Enumeration's we need to define a parser for both the path and the 
query, and for each of these we need to pass in 3 functions for each 
with only minor variations to each. Luckily, we can write a factory method 
to make this a little less tedius:

	object EnumPathAndRouteBinder {
		def binders[E <: Enumeration](enum: E): (PathBindable[E#Value], QueryStringBindable[E#Value]) = {
			/** Because I don't want to repeat a list of arguments */
			val args: (String => E#Value, E#Value => String, (String, Exception) => String) = (
				enum.withName(_),
				(e: E#Value) => e.toString,
				(k: String, e: Exception) => "Cannot parse %s as %s: %s".format(k, enum.getClass.getName(), e.getMessage())
			)
			((new PathBindable.Parsing[E#Value](_, _, _)).tupled(args), (new QueryStringBindable.Parsing[E#Value](_, _, _)).tupled(args))
		}
	}

And then call it like so outside of the enum objects:

	// you'd probably give these better names in production code
	implicit val (pathBinders1, queryBinders1) = EnumPathAndRouteBinder.binders(RequestedOrder)
	implicit val (pathBinders2, queryBinders2) = EnumPathAndRouteBinder.binders(SortingBy)
	implicit val (pathBinders3, queryBinders3) = EnumPathAndRouteBinder.binders(DataType1SortableFields)

Or you can call it _within_ the objects extending Enumeration and then just pass 
`this` to it:

	object DataType1SortableFields extends Enumeration {
		type Field = Value
		val id = Value("id")
		val someOtherField = Value("someOtherField")
		val anotherField = Value("anotherField")

		implicit val (pathBinders, queryBinders) = EnumPathAndRouteBinder.binders(this)
	}

Let me explain the enum binder factory a little bit: As you're probably aware 
if you [read my last post], nested types can't be made without a reference to 
their parent class or object. So that's why we have to pass in the object 
extending `Enumeration` to our `binders` method. Once we have it though, we 
can happily instantiate members of the inner class (whose type is `E#Value`) 
with `withName`. The odd looking: 

	((new PathBindable.Parsing[E#Value](_, _, _)).tupled(args), (new QueryStringBindable.Parsing[E#Value](_, _, _)).tupled(args))

Is taking the constructor for the two `Parsing` classes, converting them into 
partial functions, then using [Function.tupled] to pass the `args` to the 
constructor. The reason I did this is because I didn't want to write the 
same boiler plate for the parsers over and over. If this is confusing to 
you, this is the same code written without the use of `tupled`:

	def binders[E <: Enumeration](enum: E): (PathBindable[E#Value], QueryStringBindable[E#Value]) = {
		val parse: String => E#Value = enum.withName(_)
		val serialize = (e: E#Value) => e.toString
		val err = (k: String, e: Exception) => "Cannot parse %s as %s: %s".format(k, enum.getClass.getName(), e.getMessage())
		(new PathBindable.Parsing(parse, serialize, err), new QueryStringBindable.Parsing(parse, serialize, err))
	}

And with that helper object, you can more easily create bindings for your 
enumerations! Hopefully this helps.

[documentation shows in the scaladoc]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.mvc.QueryStringBindable
[read my last post]:/tech-blog/supporting-enums-in-anorm-rowparsers
[Function.tupled]:http://www.scala-lang.org/api/2.11.7/index.html#scala.Function$