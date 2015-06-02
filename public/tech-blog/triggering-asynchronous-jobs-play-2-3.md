### Triggering Asynchronous Jobs in Play 2.3

In the [old version of play it was rather easy to create jobs]. There 
was an entire package dedicated to the task in version 1.2 of the 
framework. But, with an upgrade to Play 2.3 that package disappeared! 

So then, how do you perform a job? 

Well, in 2.3 this has to be done by [integrating with Akka]. Luckily, 
the framework has a default [ActorSystem] which we can tie into easily. 

Long story short, you'll end up with code like this:

 	import play.api.libs.concurrent.Akka
  	import play.api.libs.concurrent.Execution.Implicits._

  	// code ...
  	def someControllerOrServiceMethod() {
		val myActor = Akka.system.actorOf(Props( SomeTestActor()))
		Akka.system.scheduler.scheduleOnce(0.microsecond, myActor, SomeTestActor.SomeMessage(args))
  	}

This is taking avantage of the Akka [scheduler] that is integrated into 
the Playframework. In the code above we would create an actor and 
immediately send it a message to kick off whatever it needs to do. You 
can also schedule recurring messages like so:

	// code ...
  	def someControllerOrServiceMethod() {
		val myActor = Akka.system.actorOf(Props( SomeTestActor()))
		Akka.system.scheduler.scheduleOnce(1000.microsecond, 300.seconds, myActor, SomeTestActor.SomeMessage(args))
  	}

This uses the overloaded version of `schedule` with the following signature:

	schedule( initialDelay: Duration, 
		frequency: Duration,
		receiver: ActorRef,
		message: Any
	): Cancellable

You could use this for simple clean up processes, starting the 
scheduled tasks when play boots using [GlobalSettings] like so:

	import play.api._
	import play.api.libs.concurrent.Akka
	import play.api.libs.concurrent.Execution.Implicits._

	object Global extends GlobalSettings {

	  override def onStart(app: Application) {
	    Logger.info("Application has started")
	    val myActor = Akka.system.actorOf(Props( SomeTestActor()))
		Akka.system.scheduler.scheduleOnce(1000.microsecond, 300.seconds, myActor, SomeTestActor.SomeMessage(args))
	  }

	  override def onStop(app: Application) {
	    Logger.info("Application shutdown...")
	  }

	}

The calling code isn't difficult, but you do need to provide an 
implementation of an Actor that makes sense. In the work I've done 
so far I've used self-killing Actors. Here's the basics: 

	import akka.actor.{Actor, ActorRef, PoisonPill}
	import scala.util.{Success, Failure}
	import scala.concurrent._
	import scala.concurrent.duration._
	import ExecutionContext.Implicits.global

	trait MsgSender {
		def sendMsg(msg: TestActor.InternalActorMessage)(implicit actor: ActorRef) : Unit
	}

	trait SelfSender extends MsgSender {
		def sendMsg(msg: TestActor.InternalActorMessage)(implicit actor: ActorRef) = {
			actor ! msg
		}
	}

	object TestActor {
		class InternalActorMessage() {}
		case class SomeMessage() extends InternalActorMessage
		case class OtherMessage() extends InternalActorMessage

		def apply() = {
			new TestActor() with SelfSender
		}
	}

	class TestActor extends Actor { this: MsgSender =>
		def receive = {
			case TestActor.SomeMessage => 
				// do stuff
				sendMsg(TestActor.OtherMessage())
			case TestActor.OtherMessage =>
				// do stuff
				self ! PoisonPill
		}
	}

This is a heavily stripped down version of some code I'm using. You 
might wonder why I'd abstract the sending into a trait like I did. 
The answer is: for testing! 

If you have an actor that primarily communicates with itself by sending 
messages via `self ! msg` it can be difficult to test. Since when you 
send it a message, you'll always end up at the end of the chain of events. 
In the above case, how would you test that handling SomeMessage worked? 

With the trait and mixin being done in the `apply` method of the TestActor 
companion object, we can grab our "default" Actor for use in the application 
and mix in a testing MsgSender when we unit test:

	trait TestMsgSender extends MsgSender {
		def sendMsg(msg: TestActor.InternalActorMessage)(implicit actor: ActorRef) = {
			//don't forward the message back to the actor, or send it to a 
			//test monitoring actor or whatever you'd like! 
		}
	}

	val testActor = Props(new TestActor() with TestMsgSender)

	// ... do tests with TestKit and whatnot 

By not forwarding the messages along to ourselves, we can execute and 
test _only_ the cases in the `receive` method that we want to. There 
are other ways to do this of course, such as overriding the `!` (tell) 
method and using the test probe, but I find that using trait's is easy 
to reason and understand within a test. So I've preferred that so far. 

while using jobs is not as simple as it was in version 1 of the framework, 
it still is pretty easy as long as you know the right tricks! 




[old version of play it was rather easy to create jobs]:https://www.playframework.com/documentation/1.2/jobs
[integrating with Akka]:https://www.playframework.com/documentation/2.3.x/ScalaAkka
[ActorSystem]:http://doc.akka.io/docs/akka/2.0/general/actor-systems.html
[scheduler]:http://doc.akka.io/docs/akka/2.0/scala/scheduler.html
[GlobalSettings]:https://www.playframework.com/documentation/2.3.x/ScalaGlobal
