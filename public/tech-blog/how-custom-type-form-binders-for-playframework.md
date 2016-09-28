### How to make custom type binders for Play! Forms

If you've used [play!] then you know that it comes with a number of 
[form helpers that help define the types of data in a form], such as 
`nonEmptyText`, `boolean`, `email`, and a number of others. These, as 
far as the type goes, map to normal primitives like `String`, `Long`, 
`Int`, and in the case of the `date` helpers, to [Date], [sql.Date], 
and [DateTime].

There are [Mapping]s, and then there are [Format]s. They perform similar 
methods within play, and in fact [Formatters] have a self-type of Mapping.
So what's the difference between the two? From what I can tell, a Formatter
is what's looked for when one calls `of[T]` when setting the type of a 
form element. Like so:

	import java.util.UUID

	val myForm = new Form[(String, UUID)](
		tuple(
			"str" -> text,
			"uuid" -> of[UUID]
		)
	)

`of` will look for an implicit [Format] for the type given to use when 
trying to bind and unbind the field `uuid`. This is as simple as looking 
at the trait documentation for [Formatters] and implementing it for the
type:

	import play.api.data.FormError
	import play.api.data.format.Formatter

	implicit val UUIDFormat = new Formatter[UUID] {
		def bind(key: String, data: Map[String, String]): Either[Seq[FormError], UUID] = {
			data.get(key).map(UUID.fromString(_)).toRight(Seq(FormError(key, "forms.invalid.uuid", data.get(key).getOrElse(key))))
		}
		def unbind(key: String, value: UUID): Map[String, String] = Map(key -> value.toString)
	}

The `bind` method is used to transform text data from the submitted form 
into the required type. The result of the `bind` method is an Either, 
with the failed left projection indicating a `FormError` has occured. 
The arguments to the `FormError` are similar to the arguments to defining
a custom `Constraint` in play, the `forms.invalid.uuid` indicates what
message from the Message's API will be loaded if it's in scope, and the
arguments after the hard-coded string correspond to any number of arguments
that will be interpolated by the messages parameter substitution.\*

The `unbind` method, unsurprisingly, does the opposte of the `bind` 
statement in that we convert from our type to a string so that we can 
pass the form field to any templates requiring us. map

\*<small>In a messages file, if you set something like, forms.invalid.uuid={0} is invalid, 
then you're going to see the first argument given to the FormError where that {0}
is.
</small>

	




[play!]:https://playframework.com/
[form helpers that help define the types of data in a form]:https://playframework.com/documentation/2.3.x/ScalaForms
[Date]:https://docs.oracle.com/javase/8/docs/api/java/util/Date.html
[sql.Date]:https://docs.oracle.com/javase/8/docs/api/java/sql/Date.html
[DateTime]:http://joda-time.sourceforge.net/apidocs/org/joda/time/DateTime.html
[Mapping]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.data.Mapping
[Format]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.data.format.Formats$
[Formatters]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.data.format.Formatter