### Akka DSL and Spray Routing with Cake Pattern

Today I was working my way through some [Akka tutorials] and was 
thinking to myself: _man, I wish I knew what they called each symbol!_ 
So I got to thinking, well, I'm sure others are thinking the same 
thing, why not write a quick post about it? 

One of the first things I found myself wondering when dealing with Akka 
was: _What the heck is Props?_ It wasn't until I saw this that it made 
any sense to me: 

	class Worker extends Actor {
		...
	}

	class Master(nrOfWorkers: Int, nrOfMessages: Int, nrOfElements: Int, listener: ActorRef) extends Actor {
		...
	}

	...

	val listener = system.actorOf(Props[Listener], name = "listener")
	val master = system.actorOf(Props(new Master(
		nrOfWorkers, nrOfMessages, nrOfElements, listener
	)), name = "master")

Specifically, the way that we can do both `Props[ActorClass]` and 
`Props(new ActorClassWithConstructorArgs(a,b,c))` made me realize that 
the role of `Props` was to provide a factory to create Actors. And on 
wising up and reading the [scala doc], it was pretty obvious that when 
you see `Props` you're seeing the preferred way to create Actors. 

If you look at the [scala doc] you'll see that Props takes a [Deploy] 
object which can be configured from a conf file. Of course, you won't 
often find a Props object being created without use of the factory. 
Something like this: 

	val d = Deploy(path = "/tmp/test.conf")
	val p = new Props(deploy = d, classOf[Listener], scala.collection.immutable.Seq.empty[Any])
	val s = ActorSystem()
	val a = s.actorOf(p)

Is less desireable than:

	val s = ActorSystem()
	s.actorOf(Props[Listener].withDeploy(Deploy(path="/tmp/test.conf")))

Because it's a bit easier to read and understand the factory methods.

So what's this `!` function? It's defined in the [ActorRef docs], and 
does the same thing as the `tell` function, but with an implicit 
sender instead of an explicit: 

	a ! PiApproxiation(1, Duration("1 second")

is the same as 

	a tell (PiApproxiation(1, Duration("1 second")), a)

The same can be said of the `?` function, which corresponds to the 
`ask` function. Defined in [AskableActorRef]. The example code from 
the [Akka tutorials] was simple enough to understand once the symbols 
were resolved. While I like scala's ability to provide very unique 
function names and create readable / english-like code, it does make 
it harder to search sometimes. 

The [official documentation] is the best place to read and learn about 
the various components that make up Akka, so it's well worth a look. The 
other thing I noticed, is that in most tutorials involving [Spray] and a 
[Rest Service], there is only ever a single routing trait setup, and 
not an enterprise version that has the routes seperated by their 
concerns and then mixed together via the Cake pattern.

First off, let's create a simple Spray application to show case this 
pattern. Let's say that we have one endpoint that responds to /beef/ 
and another that responds to /nog/. Obviously we don't want to mix any 
routes that are specific to beef or nog, as that would be kind of 
gross. So we'll need to create a couple things, first, a DummyActor:


	object DummyActor {
		case class Process(s: String) 
	}
	
	class DummyActor(requestContext: RequestContext) extends Actor {
		def receive = {
			case DummyActor.Process(s) => 
				requestContext.complete(s)
				context.stop(self)
		}
	}

This actor _really_ doesn't do much besides spits back the string that 
it was given, but you can imagine that in your own cases this could 
call out to services, perform business logic, or do calculations.

Next, let's talk about a simple controller for the pathing and what to 
do when we receive a request:

	trait Beef extends HttpService {
	val beefRoutes = 
		pathPrefix("beef") {
			path("cows"){
				pathEnd { 
					respondWithMediaType(`text/plain`) {
						requestContext => {
							val dummyService = actorRefFactory.actorOf(Props(new DummyActor(requestContext)))
							dummyService ! DummyActor.Process("cows")
						}
					}
				}
			} ~
			path("bulls") {
				respondWithMediaType(`text/plain`) {
					requestContext => {
						val dummyService = actorRefFactory.actorOf(Props(new DummyActor(requestContext)))
						dummyService ! DummyActor.Process("bulls")
					}
				}
			}
		}  
	}

This uses the [spray routing] DSL to define the paths _/beef/cows_ and 
_/beef/bulls_ which simply ask our DummyActor to process a string 
specific to that endpoint (so we can tell things are working). The 
tilde between the `path(...){` pieces concatenates the routes together. 
For our second endpoint, we'll have something to do with nog: 

	trait Nog extends HttpService {
		val nogRoutes = 
			pathPrefix("nog") {
				path("egg") {
					respondWithMediaType(`text/plain`) {
						requestContext => {
							val dummyService = actorRefFactory.actorOf(Props(new DummyActor(requestContext)))
							dummyService ! DummyActor.Process("eggnog!")
						}
					}
				}
			}
	}

Similar to the beef trait, this one defines a path for _/nog/egg_ 
which will return the string _eggnog!_ when matched. The next step 
after this is to use these routes! Typically, in a [Spray] application 
you'll see something like this:

	class HttpApp extends Actor with SomeTraitDefiningRoute {
		override val actorRefFactory: ActorRefFactory = context
		def receive = runRoute(route)
	}

We have two different traits to be mixed in, but `runRoute` will only 
take one route DSL! So how do we do it? Well, if you recall that we had 
two routes in the `Beef` trait connected by `~`, it may not surprise 
you to find out we can use this to join multiple route DSL's. To make 
our lives easier later on and for clarity, we'll create a new trait 
that does this:

	trait RouteService extends HttpService 
	with Beef
	with Nog
	{ 
		val route = {
			beefRoutes ~
			nogRoutes
		}
	}

Then all we have to do to have an actor run both beef and nog routes 
is: 

	class HttpApp extends Actor with RouteService {
		override val actorRefFactory: ActorRefFactory = context
		def receive = runRoute(route)
	}

Pretty simple right? Lastly, to actually have this Actor _do something_ 
we'll need to bind it via spray's http libraries:

	object HttpApp extends App {
		runserver(host=  "localhost", port = 8089)

		def runserver(host: String, port: Int) {
			implicit lazy val system = ActorSystem("HttpSystem")
			sys.addShutdownHook(system.shutdown())

			val httpActor = system.actorOf(Props[HttpApp], name = "httpActor")
			implicit val timeout = Timeout(5.seconds)

			IO(Http) ? Http.Bind(httpActor, interface = host, port = port)
		}
	}

This simply defines an object which extends `App`, therefore inherits 
a main method. We setup a shutdown hook so that when the JVM goes offline 
so does our server. Then we bind the actor to the ports specified by our 
call to runserver. 

For clarity, here's the full code including the import statements:

<script src="https://gist.github.com/EdgeCaseBerg/4e71acb59a11d6ab1464.js"></script>

And my build.sbt file looked like this for the project:

	name := "Akka Tutorial"

	version := "1.0"

	scalaVersion := "2.10.4"

	resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

	libraryDependencies ++= {
	  val sprayVersion = "1.3.1"
	  val akkaVersion = "2.3.11"
	  Seq(
	  "io.spray" % "spray-can" % sprayVersion,
	  "io.spray" % "spray-routing" % sprayVersion,
	  "io.spray" % "spray-testkit" % sprayVersion,
	  "io.spray" % "spray-client" % sprayVersion,
	  "io.spray" %%  "spray-json" % "1.2.5",
	  "com.typesafe.akka" %% "akka-actor" % akkaVersion,
	  "com.typesafe.akka" %% "akka-slf4j" % akkaVersion,
	  "com.typesafe.akka" %% "akka-testkit" % akkaVersion % "test",
	  "ch.qos.logback" % "logback-classic" % "1.0.12",
	  "org.scalatest" %% "scalatest" % "2.0.M7" % "test",
	  "com.typesafe" % "config" % "1.2.1"
	  )
	}

This is a simple introduction to using spray, scala, and Akka together 
to create a simple skeleton one can easily fill out as they go along. 
In an actual application it would be best to extract each seperate 
service (Beef and Nog) to their own files or packages as neccesary. Then 
use the traits to bind each together. This has numerous advantages, 
including: 

1. Easier for new team members to grok your code
2. Easier for you to remember where things are
3. Easier to test since each piece is seperated until glued together by traits 

Hope this has wetted your appetite for playing with some of the cooler 
libraries and frameworks out there for Scala! 


[Akka tutorials]:http://doc.akka.io/docs/akka/2.0/intro/getting-started-first-scala.html
[scala doc]:http://doc.akka.io/api/akka/2.3.1/index.html#akka.actor.Props
[Deploy]:http://doc.akka.io/api/akka/2.3.1/index.html#akka.actor.Deploy
[ActorRef docs]:http://doc.akka.io/api/akka/2.3.1/index.html#akka.actor.ActorRef
[AskableActorRef]:http://doc.akka.io/api/akka/2.3.1/index.html#akka.pattern.AskableActorRef
[official documentation]:http://doc.akka.io/docs/akka/2.2.0/scala/actors.html#Send%20messages
[Rest Service]:http://blog.michaelhamrah.com/2013/06/scala-web-apis-up-and-running-with-spray-and-akka/
[Spray]:http://spray.io/
[spray routing]:http://spray.io/documentation/1.2.3/spray-routing/#spray-routing
