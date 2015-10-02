### Spray ToResponseMarshallable "too many arguments" Error

So you've setup a [Spray] API of some kind. You've got controllers, 
JSON, all sorts of goodies. You're working happily away when a co-worker 
wants to write some tests for improper behavior. Sure! You say, and 
watch them send a request with malformed content and improper urls. 

You're suddenly looking at a _very_ plaintext output from spray that says:

    The requested resource could not be found.

Oops. Looks like you forgot to add a rejection handler! Luckily, [Johannes]
has your back, providing a useful gist. You use it as an example and write
your own, returning your own response message with a `BadRequest` status 
code.

	case MalformedRequestContentRejection(message, _) :: _ => { 					
		complete(StatusCodes.BadRequest, AwesomeResponseObject(400, RequestFailed(message)))
	}

And then your compile fails:

	[error] src/main/scala/com/example/routing/MyRoutes.scala:48: too many arguments for method apply: (v1: => spray.httpx.marshalling.ToResponseMarshallable)spray.routing.StandardRoute in trait Function1
	[error] 					complete(StatusCodes.BadRequest, AwesomeResponseObject(400, RequestFailed(msg)))

What? This rather unhelpful message is complaining because the neccesary 
magnets you need to have imported to handle the `complete` method aren't
in place. How do you get them? Simple:

	import spray.http._

I found this through some trial and error and intuition. But I'm not sure 
where in the [package] the neccesary information is defined. So I'm not sure 
how to make this import be only what is neccesary. Still, hope this helps, as
the only other person I've seen with this error did not link a solution 
but rather just [cluttered up github].


[Spray]:http://spray.io/
[Johannes]:https://gist.github.com/jrudolph/9387700
[package]:https://github.com/spray/spray/tree/master/spray-http/src/main/scala/spray/http
[cluttered up github]:https://gist.github.com/gkossakowski/10277880