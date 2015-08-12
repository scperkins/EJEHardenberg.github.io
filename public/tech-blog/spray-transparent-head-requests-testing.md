### Spray Transparent Head Requests and Testing

Recently I've been using [Spray] for API work. While doing so I've 
written a few posts like [JSON and Generic Class Serialization] and
[Logging with Spray], but the other day I ran into a weird bit of a 
nonsense and ended up [raising an issue about it on the spray-can repo].

It may just be my own poor reading comprehension, but I was quite confused 
that the feature [Transparent Head Request] can cause an untestable situation. 
As I documented in my [example repository that reproduces the error], you can 
test a `head` directive within your code and it will never actually check out 
against the Transparent Head Request behavior. 

The issue is that if you have a route which _only_ supports `head` directives, 
having the `spray.can.server.transparent-head-requests="on"` line in your 
application.conf file will result in an error. Why? Because the transparent 
head request doesn't enhance the request or handle it like a rejection catcher 
of some kind (my initial assumption), but rather _replaces_ the actual `HEAD` 
request with a `GET`!

You can see this in the [code here] that it's just copying the request into a 
`GET`. This is handy when you have a route that responds to `GET` it now also 
responds to `HEAD`. But if you head a route that is only meant for a `HEAD`
request than it will reject any `HEAD` request sent to it while you have the 
transparent requests on! In order to fix that, you need to set the transparent 
requests off, and now if you want to support `HEAD` on each of those `GET` 
routes of yours, you need to code them yourself manually.

The extra labour isn't really my issue, after all, if you're supporting `HEAD` 
requests, there's a chance that you probably don't want the same logic to be 
applied (for example if you don't want to hit your database on every `HEAD`), 
so you might be coding your `head` directives anyway. The reason why I raised 
this as [a bug] on the [spray-can repository] was because there is _absolutely 
no way to test this behavior_. 

>"That's because tests built with the testkit are executed without spray-can and so transparent-head-request handling isn't available. I agree that this is unfortunate as it prevents proper testing of the behavior." -[jrudolph]

So while you can test your code and `head` directives and the tests will tell 
you they pass, when you actually _run_ the server and send a `HEAD` request to 
one of your endpoints to check that it works. **BAM** Whatever code you're 
expecting to run on a `HEAD`-only endpoint isn't running. **And there's probably
no way you're going to know that**.\*

Best part is that transparent head requests is `on` by default. So if you're not 
aware of this by reading the [Transparent Head Request] documentation, you'll get
hit by this!

<small>\*At least not until your DBA asks why all your health checks against database intensive endpoints are triggering the database when you assured him the `HEAD` requests wouldn't do that ;)</small>


[a bug]:https://github.com/spray/spray-can/issues/27
[raising an issue about it on the spray-can repo]:https://github.com/spray/spray-can/issues/27
[Spray]:https://spray.io
[JSON and Generic Class Serialization]:/tech-blog/serializing-json-generic-classes-spray-json
[Logging with Spray]:/tech-blog/logging-to-a-file-spray-async
[Transparent Head Request]:http://spray.io/documentation/1.1.2/spray-routing/method-directives/head/
[example repository that reproduces the error]:https://github.com/EdgeCaseBerg/spray-head-error-example
[code here]:https://github.com/spray/spray/blob/ccc3f20477a0752233f19315dcbf695050c399ab/spray-can/src/main/scala/spray/can/server/OpenRequest.scala#L80
[spray-can repository]:https://github.com/spray/spray-can
[jrudolph]:https://github.com/jrudolph