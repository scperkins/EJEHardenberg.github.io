### How to use enumerations in Anorm's RowParser 

Today I was writing up a bit of code involving [anorm], and needed to 
add in an Enum type. So I looked around at the [scaladoc] a little bit 
and found that the `get` method of the [SqlParser object] takes an 
implicit `extractor` of type `Column[T]`. So I went ahead and looked at
the documentation for [Column]. I didn't find much hints to creating your 
own in the trait itself, but in the [companion object] I did find all the 
pre-defined extractors of anorm itself. One in particular caught my eye,  
the `columnToUUID` value of the object. 

Since UUID is an Enum, I figure'd I could easily lift and modify the code 
for that to do what I needed for my other types. The [source] for the it 
looks like this:

	implicit val columnToUUID: Column[UUID] = nonNull { (value, meta) =>
	    val MetaDataItem(qualified, nullable, clazz) = meta
	    value match {
	      case d: UUID => Right(d)
	      case s: String => Try { UUID.fromString(s) } match {
	        case TrySuccess(v) => Right(v)
	        case Failure(ex) => Left(TypeDoesNotMatch(s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to UUID for column $qualified"))
	      }
	      case _ => Left(TypeDoesNotMatch(s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to UUID for column $qualified"))
	    }
	  }

Which is _fairly_ easy to understand. `nonNull` is a helper defined in 
the `Column`'s companion object which handles throwing an error if the 
field is `null` when you didn't expect it to be, otherwise it executes 
the partial function you're providing it. This function simply takes 
`Any` and [MetaDataItem]. The `MetaDataItem` provides information about 
the column up for conversion and allows you to provide an error message
that's useful later on.

Looking at the code, it's pretty similar to what you might expect. 
Internally anorm uses `Left` and `Right` for parsing as well as scala's 
`util.Success` and `util.Failure` (Note here that `TrySuccess` is a type 
alias for `util.Success` because anorm [has it's own success class]). The 
only thing you really need to change here is the type parameter to `Column`
and how you convert a `String` into it. Scala Enumeration's come with a 
[withName] method that you can use where `UUID.fromString` is called. 

So if you had an enumeration in scala defined like so:

```
object MyEnum extends Enumeration {
	type MyAlias = Value
	val foo = Value("foo")
	val bar = Value("bar")
}
```

Then a parser for it would look like this:

	implicit val columnToMyEnum: Column[MyEnum.MyAlias] = nonNull { (value, meta) =>
	    val MetaDataItem(qualified, nullable, clazz) = meta
	    value match {
	      case d: MyEnum.MyAlias => Right(d)
	      case s: String => Try { MyEnum.withName(s) } match {
	        case TrySuccess(v) => Right(v)
	        case Failure(ex) => Left(TypeDoesNotMatch(s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to MyEnum.MyAlias for column $qualified"))
	      }
	      case _ => Left(TypeDoesNotMatch(s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to MyEnum.MyAlias for column $qualified"))
	    }
	  }

Which is pretty straightforward to use in a `RowParser` by calling `get` 
with your enumeration's type and having the custom Column in scope. This 
will implicitly call your defined val:

	implicit val columnToMyEnum = ...
	...
	val myRowParser = RowParser[Thing] {
      ...
      get[MyEnum.MyAlias]("mycolumnname") ~ 
      ...
	}

And you're off to the races. Now, since the code is so similar, it begs 
the question: Can we make defining arbitrary Column's for subtypes of 
Enumeration take less boilerplate? The answer is yes:

	object EnumColumn {
	  def for[E <: Enumeration](enum: E): Column[E#Value] = {
	    Column.nonNull { (value, meta) =>
	      val MetaDataItem(qualified, nullable, clazz) = meta
	      value match {
	        case d: E#Value => Right(d)
	        case s: String => Try { enum.withName(s) } match {
              case scala.util.Success(v) => Right(v)
              case Failure(ex) => Left(TypeDoesNotMatch(
                s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to ${enum.getClass} for column $qualified"
              ))
            }
            case _ => Left(TypeDoesNotMatch(s"Cannot convert $value: ${value.asInstanceOf[AnyRef].getClass} to ${enum.getClass} for column $qualified"))
          }
        }
	  }
	}

To use this, we need to pass the object extending Enumeration to our `for`
method, like so:

	implicit val enumColumnExtractor = EnumColumn.for(MyEnum)

We've now reduced a lot of boilerplates and we just have to pass our 
object to our helper method and we're good to go. Sadly, because the 
enumeration types are nested values we're not going to get much nicer 
than this, because nested types can't be made without a reference to 
their parent class, or in this case, object. Still, reducing having to 
write the amount of code for each Enumeration is valuable.


[anorm]:https://www.playframework.com/documentation/2.3.x/ScalaAnorm
[scaladoc]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.package
[SqlParser object]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.SqlParser$
[Column]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.Column
[companion object]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.Column$
[source]:https://github.com/playframework/playframework/blob/2.3.x/framework/src/anorm/src/main/scala/anorm/Column.scala#L179
[MetaDataItem]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.MetaDataItem
[has it's own success class]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#anorm.Success
[withName]:http://www.scala-lang.org/api/2.11.7/index.html#scala.Enumeration@withName(s:String):Enumeration.this.Value