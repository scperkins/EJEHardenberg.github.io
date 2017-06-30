### Playframework Optional Mappings of Objects 

The other day I was working on a form in play and fixing up some fields to go 
from being required to optional. Not an unusual thing, requirements are wrong 
all the time. But anyway, I started working on a form mapping and then had to 
work around the fact that having even one _optional_ value defined for the 
mapping meant that it required any required mappings as well. This was a problem 
because my optional field was populated by a drop down, but there was no empty 
value.

First off, here's some models to get some context if you'd like to follow along 
in a scala console. I'm using play 2.3 here though I suspect that it might not 
differ in 2.4 or 2.5 (if _you_ know, let _me_ know). 

	import play.api.data._
	import play.api.data.Forms._

	case class X(a: Option[Int], b: String)
	case class F(maybeX: Option[X])

In the above, `X` is taking on the role of the model which had gone from being 
required to being optional. So, it has some fields and then `F` is my whole 
form data object. Obviously, my real form is more complicated, but this is a simple 
minimal example to demonstrate the unintuive point I'm going to go over. 

Here's the first instinct for writing this form:

	val f = Form(
		mapping(
			"x" -> optional(mapping(
				"a" -> optional(number),
				"b" -> nonEmptyText
			)(X.apply)(X.unapply))
		)(F.apply)(F.unapply)
	)

It's a simple mapping, each element is captured in with a name matching its own 
in the respective class, and I'm using `optional` on the fields which are `Option`
in their class. Sounds good right?

**Wrong**

Here's what happens when binding some data: 

	val m1 =  Map("x.a" -> "1", "x.b" -> "hi")
	f.bind(m1).get // F(Some(X(1,hi))) (Right)

	f.bind(Map[String, String]()).get // F(None) // Right!

	val m2 = m1 - "x.b" // Lets make only that optional field be submitted!

	f.bind(m2) // form error x.b is required

As you can see, the second example shows that if you submit `x.a` then play goes 
and looks for `x.b` so it can finish mapping the `X` class. While not entirely 
wrong, it certainly seems that hey, if a field is optional, and _only the optional 
fields were submitted_, perhaps play shouldn't map the object at all?

That's the behavior I wanted at least since I didn't want to go bother a UI person
to make the form not send any value if there was no value in the other input. 
Luckily, you can get this behavior in the form mapping if you try hard enough!

	val f2 = Form(
		mapping(
			"x" -> tuple(
				"a" -> optional(number),
				"b" -> optional(nonEmptyText)
			).transform(
				{ 
					case (maybeA, Some(b)) => Option(X(maybeA,b))
					case (_, _) => Option.empty[X]
				},
				(x: Option[X]) => (x.flatMap(_.a),x.map(_.b))
			)
		)(F.apply)(F.unapply)
	)

So, now the base form mapping uses the `tuple` helper (because I'm too lazy to 
write an intermediate case class to use for this) and then we `transform` it in 
order to apply out own rules in how it should become an `Option[X]`. The `transform`
method takes in two arguments, both functions. One that tells the system how to 
convert the given type (`Tuple2` in this case) into some other type (`X`), and 
one that does the reverse. 

With that in place we can see the behavior we want:

	f2.bind(m1).get // F(Some(X(1,hi)))

	f2.bind(m1 - "x.a").get // F(Some(X(None,hi)))

	f2.bind(m1 - "x.b").get // F(Some(X(None,hi)))

	f2.bind(Map[String,String]()).get // F(None)

And it still handles errors as we'd want it to:

	f2.bind(m1 + ("x.a" -> "crap"))  //FormError(x.a,List(error.number),List())

Great! Applying `transform` is useful for making decisions about your form and 
how it should map into a data class you'll use in the rest of your application. 
And with the above trick, you can easily handle a drop down that always submits 
to the backend. Before closing, its worth mentioning that there's also a `verifying`
method you can use to check arbitrary conditions. For example, if there _was_ a 
non-value to be submitted from the dropdown, but I wanted to enforce that the 
form handled data only when _both_ were submited OR when they both weren't, then 
I could use verifying to do that in a simple way. So, with the models like:

	case class Y(a: Int, b: String)
	case class F2(maybeY: Option[Y])

I could use the form mapping with `transform` and `verifying` like so:

	val f2 = Form(
		mapping(
			"y" -> tuple(
				"a" -> optional(number),
				"b" -> optional(nonEmptyText)
			).verifying(
				"If you enter a value for a you must enter one for b and vice verse", 
				t => t._1.isDefined == t._2.isDefined
			).transform(
				{ 
					case (Some(a), Some(b)) => Option(Y(a,b))
					case (_, _) => Option.empty[Y]
				},
				(y: Option[Y]) => (y.map(_.a),y.map(_.b))
			)
		)(F2.apply)(F2.unapply)
	)

Then when submitting data you'd get the desired behavior and a useful error message:

	val m3 = Map("y.a" -> "1", "y.b" -> "yay")

	f2.bind(m3).get // F2(Some(Y(1,yay)))

	f2.bind(m3 - "y.a") // FormError(y,List(If you enter a value for a you must enter one for b and vice verse),WrappedArray())

	f2.bind(m3 - "y.b") // FormError(y,List(If you enter a value for a you must enter one for b and vice verse),WrappedArray())

	f2.bind(Map.empty[String, String]).get // F2(None)

I hope this is useful to you! I'm somewhat curious if there's a way to make a field 
mapping that maps an object to None if no required fields are submitted, but right 
now I don't think I have the time to explore it. If I do I'll update this post 
though! 