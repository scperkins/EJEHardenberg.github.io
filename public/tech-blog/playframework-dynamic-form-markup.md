### Indices in Play!'s form helpers. Do they matter?

So the other day my team and I were working on a bunch of forms that had 
dynamically added/removed elements. Questions came up about how Play! 
generates the indexes for repeated fields and how we should emulate the 
functionality when adding in new mark up from the client side.

Unfortunately, the [documentation for Play! 2.3] only says this about 
repeated value field names:

>When you are using repeated data like this, the form values sent by the browser must be named emails[0], emails[1], emails[2], etc.

There's also [a small section in 2.4's documentation] which hints at more:

>When you are using repeated data like this, there are two alternatives for sending the form values in the HTTP request. First, you can suffix the parameter with an empty bracket pair, as in “emails[]”. This parameter can then be repeated in the standard way, as in http://foo.com/request?emails[]=a@b.com&emails[]=c@d.com. Alternatively, the client can explicitly name the parameters uniquely with array subscripts, as in emails[0], emails[1], emails[2], and so on. This approach also allows you to maintain the order of a sequence of inputs.

But, if you look at the [source code for 2.3], it also supports the numberless names:

	def bindFromRequest(data: Map[String, Seq[String]]): Form[T] = {
	  bind {
	    data.foldLeft(Map.empty[String, String]) {
	      case (s, (key, values)) if key.endsWith("[]") => s ++ values.zipWithIndex.map { case (v, i) => (key.dropRight(2) + "[" + i + "]") -> v }
	      case (s, (key, values)) => s + (key -> values.headOption.getOrElse(""))
	    }
	  }
	}

Which means that you can do things like this:

	import play.api.data._
	import play.api.data.Forms._

	val f = Form(single("s" -> seq(boolean)))

	f.bindFromRequest(Map("s[]" -> Seq("true", "false","true"))).get
	// Seq[Boolean] = List(true, false, true)

And not have to worry about the numbers inbetween. This is great and all, 
but if you're using the play helpers you're unlikely to ever even realize 
you can do this if you don't see the note about it. Why? Because the 
form helpers will _never_ generate indexless names for your fields since
the [RepeatedMapping.unbind method] adds in the indices. 

Another important thing to note about the `seq` mapping (which is derived 
from the `RepeatedMapping` class) is that the index's you send for each 
object that's mapped _must_ be unique! If you submit two inputs that have 
the name `email[1]` then only one of those will be bound. This is indicated 
by the binding code which calls [RepeatedMapping.indexes], which looks like 
this:

	def indexes(key: String, data: Map[String, String]): Seq[Int] = {
	    val KeyPattern = ("^" + java.util.regex.Pattern.quote(key) + """\[(\d+)\].*$""").r
	    data.toSeq.collect { case (KeyPattern(index), _) => index.toInt }.sorted.distinct
	}

Notice the `distinct`? That means no multiples! So these two things combined 
means you have two options:

1. Generate HTML with form helpers and then make sure to update indices for names in JS for dynamically added elements
2. Generate HTML without the form helpers using the `[]` syntax and pray that you don't have any complex mappings.

What I mean by a complex mapping is something like this:

	def foo: Mapping[Foo] = mapping(
		"id" -> uuid,
		"value" -> nonEmptyText
	)(Foo.apply)(Foo.unapply)

Why? Because say you were to put this into a repeated context like:

	object RepeatedFoos {
		def newForm(): Form[Seq[Foo]] = Form(single("foos" -> seq(foo)))
	}

When you generate HTML without indices you'll get names like:

	foos[].id = XXX
	foos[].value = YYY
	foos[].id = ZZZ
	foos[].value = WWW

And play doesn't actually handle this in the case of custom object mappings. 
[I tested this] and it only seems to work in the [case of a simple field]. 
So keep that in mind, if you're dynamically adding a simple field you can 
use the [] method and not have to worry about too much complexity. For complex
objects, read on.

So my team elected to go with the first option listed above. And we wrote 
some pretty nice code to handle things generically. And I've teased out 
the main idea of it into some example code that you can [look at here]. 

An interesting thing to note, and probably one of the first questions that 
comes to mind for someone about to add in new markup from the front end 
without help from play would be:

>Do the indices in field names matter in play?

As in, do they need to be sequential? Do I need to keep them in order? 
What happens if I don't? If you take a second look at the `KeyPattern` 
that's used by [RepeatedMappings.indexes] you'l see

	val KeyPattern = ("^" + java.util.regex.Pattern.quote(key) + """\[(\d+)\].*$""").r

Which is only matching numbers, it's not checking anything else about them. 
And in the `bindFromRequest` method we mentioned above we're just sorting 
and unduplicating data being bound. Which all boils down to *no. The actual 
index of a playframework field name does not matter*. Its only purpose is 
to provide a key for any related information (such as our `id` and `value` 
fields for `Foo` we used above as an example). So any javascript code 
or custom HTML generation you write can use arbitrary numbers as long as 
you're consistent. This is illustrated in the [second example here].

The last question you might ask yourself is: _If I have a simple field, 
can I mix both the indexed and the non-indexed field names?_. The answer,
unsurprisingly, is no you can't. One will overwrite the other. This isn't 
surprising because if you pay attention to the bind code

	def bindFromRequest(data: Map[String, Seq[String]]): Form[T] = {
	  bind {
	    data.foldLeft(Map.empty[String, String]) {
	      case (s, (key, values)) if key.endsWith("[]") => s ++ values.zipWithIndex.map { case (v, i) => (key.dropRight(2) + "[" + i + "]") -> v }
	      case (s, (key, values)) => s + (key -> values.headOption.getOrElse(""))
	    }
	  }
	}

you'll note we're folding over a `Map`, and in the case of the same key 
being present, new values overwrite the old. So if you were to submit 
`field[0]` and field[]` in that order, then you'd only end up with `field[]`
values since the other was overwritten. An example of [this behavior is here].

And with that question answered we're done! To recap:

- Play's form helpers can bind to either `[]` or to `[#]` for _simple_ fields, not to both
- Play's `[]` _cannot_ handle custom mappings of case classes.
- The actual number between the brackets in a field name _does not matter_ so long as its a number. Its only purpose is to group nested data together (if that's the case)

One thing I didn't touch in this blogpost is dealing with dynamically generated 
HTML for nested fields (inputs with names like `foo[0].bars[3].id`). They're not 
that different, but you do need to keep in mind that the right index must change 
if you were to do something like move one `bar` to another `foo`. I might update
the example code I've linked to in this blog with an example of this if someone 
asks.


[documentation for Play! 2.3]:https://playframework.com/documentation/2.3.x/ScalaForms#Repeated-values
[a small section in 2.4's documentation]:https://playframework.com/documentation/2.3.x/ScalaForms#Repeated-values
[source code for 2.3]:https://github.com/playframework/playframework/blob/34b3090525c4b550938121beb09f10072811b1f3/framework/src/play/src/main/scala/play/api/data/Form.scala#L90
[RepeatedMapping.unbind method]:https://github.com/playframework/playframework/blob/34b3090525c4b550938121beb09f10072811b1f3/framework/src/play/src/main/scala/play/api/data/Form.scala#L726
[RepeatedMapping.indexes]:https://github.com/playframework/playframework/blob/34b3090525c4b550938121beb09f10072811b1f3/framework/src/play/src/main/scala/play/api/data/Form.scala#L711
[look at here]:https://github.com/EdgeCaseBerg/play--repeated-form-examples
[second example here]:https://github.com/EdgeCaseBerg/play--repeated-form-examples/blob/master/public/javascripts/repeatFoos-ex2.js#L24
[I tested this]:https://github.com/EdgeCaseBerg/play--repeated-form-examples/blob/master/app/views/example/repeatedFoosEx3.scala.html
[case of a simple field]:https://github.com/EdgeCaseBerg/play--repeated-form-examples/blob/master/app/views/example/simpleNoIndicesEx1.scala.html
[this behavior is here]:https://github.com/EdgeCaseBerg/play--repeated-form-examples/blob/master/app/views/example/simpleMixedIndicesEx1.scala.html