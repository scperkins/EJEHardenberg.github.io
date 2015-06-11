### Reverse routing with Packaged Controllers in Play

#### TL;DR;

** Use the fully qualified package name of your controller package followed by routes, then your class and method to perform reverse routing in a template to a controller action**

#### Reverse Routing to Controller Actions in Play 2.3 templates

Coming from an enterprise java world, you may be used to seeing long package 
names like: `com.example.some.thing.and.stuff`, after all, [it's enterprise] 
and that means we can't have conflicts with any other namespaces. So we use 
long crazy package names. Of course, we use long package names for other 
reasons, but that's my favorite. 

In [Play], the convention for controllers is to simply be in the package called 
`controllers`. And so long as you obey this convention, you won't run into any 
issues. Of course, I wouldn't be writing this blog post if I felt like obeying 
conventions! Let's say you have a controller enterprisely namespaced: 

	package com.ethanjoachimeldridge.scala.controllers

	import play.api._
	import play.api.mvc_

	object Application extends Controller {
		def index : Action[AnyContent] = Action {
			Ok(views.html.index())
		}

		def smile : Action[AnyContent] = Action {
			Ok("Alrighty! =D")
		}
	}

And the view file:

	@()

	<html>
		<head>
			<title>Reverse Routing Demo</title>
		</head>
		<body>
			<h1>Demo!</h1>
			<a href="#????">I just want to smile!</a>					
		</body>
	</html>

Assuming you've got `build.sbt` and `plugins.sbt` setup, having files like this 
in your project will compile if you're hoping to follow along. You might notice 
the `#????` in the anchor tag. What to put here is the main subject of this 
post! 

According to the [documentation] you'd expect to write `controllers.routes.Application.smile` 
here. Of course, if you do that you'll be greeted by a fun error:

	value Application is not a member of object controllers.routes

"What gives!" You exclaim, wondering why the documentation has lied to you. So 
you give it another go, reasoning that perhaps your invokation was wrong and 
you need something different. So you might try:

	<a href="@controllers.routes.com.ethanjoachimeldridge.scala.controllers.Application.smile">

But of course this will fail as well. Any notion of a framework wide controller 
package gone, you reason again wondering if the routes are contained in your 
Application class by some extension magic:

	<a href="@com.ethanjoachimeldridge.scala.controllers.Application.routes.smile">

Which will of course fail. Not to give up, you look in the `target` directory of 
your project and find the following:

	target/scala-2.10/src_managed/main/controllers/routes.java
	target/scala-2.10/src_managed/main/com/ethanjoachimeldridge/scala/controllers/routes.java

Woah! So you realize that Play has generated a routes object for your 
controller package and try that out in your code:

	<a href="@com.ethanjoachimeldridge.scala.controllers.routes.Application.smile"
		I just want to smile!
	</a>

And all the compilation errors go away and you're happy. On thinking about this 
it makes perfect sense that the routes package is added to whatever controller 
package you're using. However the documentation doesn't actually mention this, 
or provide any examples of this. Seeming to assume that all users will use the 
conventional top level controllers package. The documentation somewhat hints at 
this:

>For each controller used in the routes file, the router will generate a ‘reverse controller’ in the routes package, having the same action methods, with the same signature, but returning a `play.api.mvc.Call` instead of a `play.api.mvc.Action.`

But doesn't explicitly say that the routes package _will be generated with the 
same package hierarchy as your controller_. Regardless, now you know how to use 
reverse routing within your templates or controllers appropriately when you're 
using a non-standard package in a play app!

[it's enterprise]:https://github.com/EnterpriseQualityCoding/FizzBuzzEnterpriseEdition
[Play]:https://www.playframework.com
[documentation]:https://www.playframework.com/documentation/2.3.x/ScalaRouting#Reverse-routing
