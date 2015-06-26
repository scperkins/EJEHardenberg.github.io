### Type Erasure, Option, and Folding 


#### The Tl;dr

If you get `error: type mismatch;` while specifying `None` as the
default in a `.fold` on an `Option`. Use a closure in your default case
and specify the type like so: `option.fold { val thing = Option[MyType]
= None; thing } { ... }`

#### Long Story:

Everyone likes type inference. It saves a lot of writing on a
programmers part when instead of writing a behemoth of some kind like
this: 

	val i : Future[Option[my.package.model.ObjectThing]] = someMethod

and can instead just write:

	val i = someMethod

And the compiler keeps track of your type for you. It's handy, and
something Haskell, OCaml, and Scala (among others) enjoy. However, type
inference isn't always as easy as reading a method's return type. Take
this example: 

	val s : Option[Int] = someMethod()
	val r = s.fold( 0 ) { x =>
		x +  1
	}

What's the type of `r` in this case? Easy! It's an Integer! I only
recently discovered the idiom of folding on options, so let me describe
what's going on here. First, `fold` is often seen as a way to implement
a reducing operation on a list: 

	val myList = List(1,2,3)
	val q = myList.fold(0) { (l, r) => l + r } 
	// q is 6

`q` is 6 in this case because we _start_ at 0, and then take our current
left value (which is 0 at first) and then add it to the next element in
our list, 1. On the next iteration the `l` will be the result of our
previous computation (1), and we'll add 2. The result being 3, we'll
then have 3 as our `l` value and the last element in the list (3) as
`r`. Lastly, we'll do our add again and `q` will be the result of 3 + 3. 

So what's up with that `fold` on the `Option` class then? Well, besides
that the community in scala in split between [sticking to getOrElse] and 
[using fold on option], it's a handy and _type safe_ way of dealing with
options. A complaint levied against using `fold` is that the order isn't
the same as `getOrElse`:

	val o = Option[Int] = None
	o.getOrElse(2) // yields 2 
	o.fold(2)( x => x) // yields 2

Having the default first seems to throw people off. But here's why I
think it makes sense. In the case of our reduce example, we _seeded_ the
left hand side of our function with the _first_ set of parameters. In
the case of folding our option, we _seeded_ our result, if it didn't
have a value already. When I think of it this way, it's easy to get into
the habit of staying consistent with our folds. 

Moving back to our point about type inference, can you tell me what the
type of `s` is? 

	val o = Option[Int] = None
	val s = o.getOrElse("hi")

If you said: `String` congratulations! **You're wrong**. The correct
type is `Any`. Why? Because o would give us an Int if it had a value,
and `String` if it didn't, but since we don't know (assume `o` came from
`someMethod`) until runtime, the compiler has to default to the common
base type, which in the case of `Int` and `String` is `Any`. But Ethan,
you say, you said `fold` is safer? Yup. Let's try the same with fold: 

	val o = Option[Int] = None
	val s = o.fold("hi") { x => x }
	
	<console>:8: error: type mismatch;
	found   : Int
	required: String
     	val s = o.fold("hi") { x => x }

So now instead of having to deal with `Any` and losing our type, we get
a compiler level error that tells us that we might want to be more
careful and return the same type so we can reason about it easier. In
the case of `Option.fold`, the default will determine which type the
compiler requires. 

Now to the reason I'm writing this blog post: What do you about type
erasure when dealing with a class wrapped in Option? To make what I'm
asking clear, let's say you have this:

	val o = Option[Int] = ??? //pick Some(1) or None
	o.fold(None) { x => Some(x) }

The above will not compile. In fact, you'll get the following error
message:

	error: type mismatch;
	  found   : Some[Int]
	  required: None.type

Confused? After all, you can assign none to an `Option[Int]`, so why is
the compiler so strict and how do you get around it? You might think
specificying the result of `o.fold` would help. Nope. Here's a hack
around it: 

	val o = Option[Int] = ???
	o.fold { 
		val tmp : Option[Int] = None
		tmp
	} { x => Some(x) } 

By doing the above, we let the compiler figure out that yes, the two
types in both closures of the fold match. And they match because we now
have a common ancestor type:

	scala> val o : Option[Int] = None
	scala> o.getClass()
	scala> res6: Class[_ <: Option[Int]] = class scala.None$

    scala> val o : Option[Int] = Some(1)
	scala> o.getClass()
	res7: Class[_ <: Option[Int]] = class scala.Some

Notice the `Class[_ <: Option[Int]]`? That's how you can tell that they
both are descendents of `Option[Int]`. If you check the class of None:

	scala> val x =None	
	scala> x.getClass()
	res8: Class[_ <: None.type] = class scala.None$

you'll see what should be obvious by now, that they don't share the same
common base. 

I hope this helps anyone else who runs into type mismatch errors from
the None.type while folding Option instances! 



[sticking to getOrElse]:http://kwangyulseo.com/2014/05/21/scala-option-fold-vs-option-mapgetorelse/
[using fold on option]:https://groups.google.com/forum/#%21topic/scala-language/35EcioxSQ50
