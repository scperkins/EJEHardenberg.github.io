### Circe Examples

I've used a few JSON libraries in scala and most of the time end up using 
[play-json] because if I'm working in a play application, then its already
there and easy to use. However, there are limitations that make one go out 
and find an alternative sometimes. For example:

- Needing to use the same json serialization between different versions of play applications
- Needing support for flat classes that have more than 22 fields without a lot of boilerplate

One such alternative is a very nice little library called [circe]. It has a 
[simple six part guide] that serves as an introduction to using the library
but anything more complex than that and you're left to hunting through the 
[api documentation] for answers. And well, sometimes the answers aren't 
immediately obvious. The best place to get help for when this occurs is the
[gitter channel] because generally someone can help you and more often than 
not that someone is [Travis Brown] who created the library.

In this blog post, I'll document a few things that I've had to do in circe 
that don't appear in the guide I linked to, but which you might need to do 
in your own projects.

#### Setup

Before I show any examples, if you want to follow along or run these examples
in your console you'll need to setup a few imports and a build file. 

_build.sbt_

```
scalaVersion := "2.11.8"

val circeVersion = "0.8.0"

libraryDependencies ++= Seq(
  "io.circe" %% "circe-core",
  "io.circe" %% "circe-generic",
  "io.circe" %% "circe-parser"
).map(_ % circeVersion)
```

_import these in your console_

```
import io.circe._
import io.circe.generic.semiauto._
import io.circe.generic.decoding.DerivedDecoder
import io.circe.generic.encoding.DerivedObjectEncoder
```

or in one line:
```
import io.circe._, io.circe.generic.semiauto._, io.circe.generic.decoding.DerivedDecoder, io.circe.generic.encoding.DerivedObjectEncoder
```

And now you're ready to work with the examples. 

#### Recursive decoder gotchas

Consider the recursive class

```
case class A(id: Int, children: Vector[A])
```

The fact that this class is recursive isn't really a problem for circe, however 
it is a problem for the _compiler_ if you don't provide enough hints to it to
figure out what you want it to be done. Type the following into your console to 
use circe's semi-automatic deriviation to create a decoder:
```
implicit val d = deriveDecoder[A]
```
You'll get an error like this:
```
error: could not find Lazy implicit value of type io.circe.generic.decoding.DerivedDecoder[A]
```
So you read this error and think to yourself, _"oh it right, it needs to be Lazy 
since it's recursive, that makes sense!"_ so you try this:
```
lazy implicit val d = deriveDecoder[A]
```
But you'll get the same error. The _real_ problem is something similar to what 
happens when you do something like this:

```
scala> def f(x: Int) = if (x < 0) true else f(x - 1)
<console>:19: error: recursive method f needs result type
```

The compiler needs to know exactly what the type of this recursive thing is. So
if you write your decoder like so:
```
scala> implicit val d: Decoder[A]  = deriveDecoder[A]
```
You'll be happily treated to seeing it compile and the console spit back
```
d: io.circe.Decoder[A] = io.circe.generic.decoding.DerivedDecoder$$anon$1@78952c43
```

Simple enough, but very easy to get tripped up. For example, if you remove the 
implicit keyword from the declaration, you'll end up with that same error again. 

#### Handling recursive decoding yourself 

So say you don't want to use the semi-automatic derivation, maybe you have some 
rules you want to apply during the decoding process and fail it if it doesn't 
quite fit what you want. Let's look at our example class again: 

```
case class A(id: Int, children: Vector[A])
```

Let's say that our system requires that all `id`s must be greater than 0. And 
we've decided to enforce this at the json layer and reject requests before they 
even make it into the system. So we begin defining these things like so:

```
import cats.syntax.either._ // Make Either right biased

implicit val decoder: Decoder[A] = Decoder.instance { hCursor =>
	val idDecodingResult = hCursor.downField("id").as[Int] match {
		case Right(id) if id > 0 => Right[DecodingFailure, Int](id)
		case Right(id) => Left(DecodingFailure("Id must be greater than 0", hCursor.history))
		case l => l
	}
	val childrenResult = hCursor.downField("children").as[Vector[A]]
	for {
		id <- idDecodingResult
		children <- childrenResult
	} yield A(id, children)
}
```

And we can see that it works:
```
scala> parser.parse("""{"id": -1, "children": []}""").right.get.as[A]
res3: io.circe.Decoder.Result[A] = Left(DecodingFailure(Id must be greater than 0, List()))
```

However, there is one limitation here which we can see if one of the recursive 
children is invalid:

```
scala> parser.parse("""{"id": 1, "children": [{"id" : 2, "children": []},{"id": -2, "children": []}]}""").right.get.as[A]
res8: io.circe.Decoder.Result[A] = Left(DecodingFailure([A]Vector[A], List(MoveRight, DownArray, DownField(children))))
```

If you look at the operations captured in the history you can see that circe has 
told you exactly where the problem was, namely the second child of the object. 
But you might also see the weird message of `[A]Vector[A]` where before we saw 
the nice human friendly error message we wrote. This is a bug, and until the 
[issue] is closed you'll have to live with it. 

#### Letting circe do most of your work 

In the above example writing a decoder is simple, and part of this is because 
our toy model `A` is only two fields. However, in the real world you might have 
many more fields to deal with, and it's tedious and error prone to write them 
all out yourself. So, rather than create the entire decoder ourselves we can 
use the semi-automatic derivation and the method `emap` to construct something 
similar to the above. 

```
def validA(a: A): Boolean = {
	a.id > 0 && a.children.map(validA).foldLeft(true)(_ && _)
}

implicit val d: Decoder[A] = deriveDecoder[A].emap { a =>
    if(!validA(a)) {
        Left("Id must be greater than 0")
    } else {
        Right(a)
    }
}
```

This is a little more concise than previous code because we are now dealing with 
the parsed instance of `A` rather than the cursors within circe directly. So you 
basically now have 2 steps in the validation process, the reading of JSON, and 
the extra validation of it. If performance is a concern you probably want to 
stick with staying within circe, but if its not then the above would work fine.
However, it has the same problems as I mentioned with the above, at least until 
the [issue] is fixed:

```
scala> parser.parse("""{"id": 1, "children": [{"id" : 2, "children": []},{"id": -2, "children": []}]}""").right.get.as[A]
res0: io.circe.Decoder.Result[A] = Left(DecodingFailure([A]Vector[A], List(MoveRight, DownArray, DownField(children))))

scala> parser.parse("""{"id": -1, "children": []}""").right.get.as[A]
res1: io.circe.Decoder.Result[A] = Left(DecodingFailure(Id must be greater than 0, List()))
```

#### Handling classes with defaults on non-optional fields

[play-json]:https://www.playframework.com/documentation/2.4.x/ScalaJson
[circe]:https://github.com/circe/circe
[simple six part guide]:https://circe.github.io/circe/parsing.html
[api documentation]:https://circe.github.io/circe/api/
[gitter channel]:https://gitter.im/circe/circe
[Travis Brown]:https://github.com/travisbrown
[issue]:https://github.com/circe/circe/issues/643