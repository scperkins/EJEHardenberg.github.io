### Javascript Configuration and Play

If you're doing anything more complicated than fancy ui tricks with 
javascript there's a good chance you might eventually need some kind 
of configuration object. An obvious example is setting a google 
analytics token. The legacy way to do this might be something like:

	<script type="text/javascript">

	  var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', 'UA-XXXXX-X']);
	  _gaq.push(['_trackPageview']);

	  (function() {
	    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();

	</script>

The `UA-XXXXX-X` is specific to your token that google gives you. But, 
let's say you're creating an application that has multiple environments.
Like a staging environment that your developers use to perform final 
checks against real data before deploying code to production, or an 
integration environment where new features are tested in isolation. 
Obviously, you don't want any tracking of your QA testers to be mixed in 
with your real user's data. So you'd want to have a different token. In 
a play template you might have a simple partial like this: 


	@(gaToken: String)
	@* views/partials/ga.scala.html *@
	<script type="text/javascript">

	  var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', '@gaToken']);
	  _gaq.push(['_trackPageview']);

	  (function() {
	    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();

	</script>

The only difference of course is that we now have a variable being passed. 
This will let us load a new token based on a value in the backend, probably 
listed in the [configuration] of your application. This will work for most 
cases where you need to have some variable be used in the front end. But 
what about when you need configuration directly in a file itself?

For example, if you have a more complicated javascript based application 
you might use [gulp] or some [other build system] to compile multiple 
files together, run tests, and eventually create a single javascript bundle 
to be deployed. You can store configuration in your application of course, 
and have multiple build tasks to create different bundles for different 
environments. But this, frankly, can be annoying. You might ask yourself, 
why can't I just have my configuration managed outside of my app? 

The answer is, well of course you can. You can make XHR requests to your 
backend to get settings for a user or whatever you need. But then you're 
costing yourself two round trips. Once to load the configuration, and once 
to actually run whatever needed it! In this day and age we all love to 
have things that are _fast_. And having to have a user wait for two requests
to come back before whatever your fancy app does just won't satisfy that. 

With play, we _can_ do something about this. If your javascript is being 
served by play, you're probably using the [Assets controller]. But, if you 
really wanted to, you could serve your file our of a normal controller 
method. After all, it's just a file:

	def myStaticRessource() = Action { implicit request =>
	  val contentStream = this.getClass.getResourceAsStream("/public/my.js")
	  Ok.feed(Enumerator.fromStream(contentStream)).as("application/javascript")
	}

Or you could use the Assets controller if you don't want to use the 
`getResourceAsStream` method and rely on the classpath:

	def myStaticRessource() = Action { implicit request =>
		Assets.at("/public", "my.js")(request)
	}

The key to this, is that your configuration and your file can be 
served together. Play's HTTP bodies are [Enumerators] which means 
they can be combined. So, if your application depends on a JSON 
object as configuration, you could attach said object as part of
the script! This could be done like so:

	package controllers

	import play.api._
	import play.api.mvc._
	import play.api.libs.iteratee._
	import scala.concurrent.ExecutionContext.Implicits.global

	object MyController {

		lazy val applicationJs = _root_.controllers.Assets.
			at("/public", "my.js")

		def configFor(someId: String) = Action.async { implicit request =>
			val exampleConfigString = s"""
				var config = {
					... //myconfig that is specific to @someId
				};
				""".getBytes
			applicationJs.apply(request).map { applicationAsset =>
				val config = Enumerator(exampleConfigString)
				val jsFile = applicationAsset.body
				val resultBody = config andThen jsFile
				Ok.feed(resultBody).as("application/javascript")
			}
		}

	}

This would allow the `my.js` file to use the config object defined by the 
controller. If you were to import the `play.api.libs.json` package you 
could serialize a config case class or map into a configuration object 
directly. Then you're able to serve both files out at the same time. 

Hope this is useful!


[configuration]:https://www.playframework.com/documentation/2.3.x/Configuration
[gulp]:http://gulpjs.com/
[other build system]:https://jezenthomas.com/the-worlds-most-boring-build-system/
[Assets controller]:https://www.playframework.com/documentation/2.3.x/Assets
[Enumerators]:https://www.playframework.com/documentation/2.3.x/Enumerators
