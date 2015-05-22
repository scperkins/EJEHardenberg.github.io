### Non Empty lists validation in PlayFramework 2.3

[Play] has a lot of nice features built into it. One of them is form 
validation. It does this by letting you define mappings for forms:

    val myForm = Form(
    	mapping(
    		"somefield" -> someDataType
    	)
    )(CaseClass.apply)(CaseClass.unapply _)

There's [documentation] on the basic use cases, such as making sure 
text fields aren't empty when submitted, or that integer values are 
within the proper range. One thing that isn't in the provided 
constraint validations is the ability to check if a list is empty or 
not. 

It's not too difficult to define your own constraints, you simply need 
to create a [Constraint] of the appropriate type which has an appropriate 
method for determining whether the constraint is valid or not. The code 
performing the verification should return a `ValidationResult`,
(specifically `Valid` or `Invalid` from the `play.api.data.validation` 
package). In code:

	def nonEmptyList[T]: Constraint[List[T]] = Constraint[List[T]]("constraint.required") { list =>
    	if (list.nonEmpty) Valid else Invalid(ValidationError("error.required"))
  	}

Once you've defined your validation function it is easy to use it in 
your `.verifying` clauses in form mappings:

	val myFormWitList = Form(
    	mapping(
      		"listItems" -> list(nonEmptyText).verifying(nonEmptyList)
    	)(CaseClassFormData.apply)(CaseClassFormData.unapply _)
  	)

The above would give us a form validating that the form we submitted 
looked something like this:

	<form>
		<input type="text" name="listItems[]" />
		<input type="text" name="listItems[]" />
		<input type="text" name="listItems[]" />
		<!-- etc... -->
	</form>

Note that you **do** need the name for a repeated form element to have 
the `[]` at the end or _Play won't recognize or bind it_. Putting these 
all together we have: 

	package validations.forms

	import play.api.data.Form
	import play.api.data.Forms._
	import play.api.data.format.Formats._
	import play.api.data.validation.{Constraint,ValidationError,Valid,Invalid}


	case class MyFormData(paths: List[String])

	object ExampleForm {

	  def nonEmptyList[T]: Constraint[List[T]] = Constraint[List[T]]("constraint.required") { o =>
	    if (o.nonEmpty) Valid else Invalid(ValidationError("error.required"))
	  }

	  val exampleForm = Form(
	    mapping(
	      "items" -> list(nonEmptyText).verifying(nonEmptyList)
	    )(MyFormData.apply)(MyFormData.unapply _)
	  )
	}

Pretty simple right? We can easily right custom constraints to support 
any logic our forms might need, verifying Enumerated values, making sure 
that we've actually submitted multiple elements to an endpoint, checking 
that the username matches some custom validation. You name it, you can 
validate it. 

[Play]:http://playframework.com
[documentation]:https://www.playframework.com/documentation/2.3.x/ScalaForms
[Constraint]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.data.validation.Constraint
