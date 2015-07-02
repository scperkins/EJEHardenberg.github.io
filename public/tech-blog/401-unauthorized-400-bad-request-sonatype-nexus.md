### 401 Unauthorized and 400 Bad Request in Sonatype Nexus OSS

Today I was searching for a artifact repository to use in development, and was 
evaluating [Sonatype's Nexus]. Besides the [fantastic documentation], the application 
itself seemed to have a good community supporting it. So, I decided to download 
and give it a try. It was easy to follow the [installation manual] and within 5 
minutes I had everything installed and was ready to rumble. Here's a couple notes:

1. **Don't run Nexus as root**. It's a security issue. Make a user for them instead, or run it as your user in a home folder somewhere. 
2. **Read through the documentation**, at least the first few chapters to get the concepts down. 
3. **Change the default passwords if this isn't a local nexus and can be reached within a network**

Working with [SBT] was what I was interested in, and luckily Nexus has a 
chapter [specifically on just that]. Which got me mostly up and running. My 
build file ended up looking like this: 

	organization := "test"

	name := "thing"

	version := "0.0.1"

	scalaVersion := "2.10.3"

	scalacOptions += "-deprecation"

	libraryDependencies <+= (scalaVersion)("org.scala-lang" % "scala-compiler" % _)

	resolvers += "Nexus" at "http://localhost:8081/nexus/content/groups/public"

	credentials += Credentials(Path.userHome / ".ivy2" / ".credentials")

	publishTo <<= version { v: String =>
	  val nexus = "http://localhost:8081/nexus/"
	  if (v.trim.endsWith("SNAPSHOT"))
	    Some("snapshots" at nexus + "content/repositories/snapshots")
	  else
	    Some("releases" at nexus + "content/repositories/releases")
	}

With a _.ivy2/.credentials_ file:

	realm=Sonatype Nexus Repository Manager
	host=127.0.0.1
	user=admin
	password=admin123

I spent a lot longer than my initial 5 minutes on trying to get the `publish` 
task in sbt to run though. I kept getting:

	> publish
	[info] Wrote /Users/eeldridg/Sites/thing/target/scala-2.10/thing_2.10-0.0.1.pom
	[info] :: delivering :: test#thing_2.10;0.0.1 :: 0.0.1 :: release :: Thu Jul 02 11:56:02 EDT 2015
	[info] 	delivering ivy file to /Users/eeldridg/Sites/thing/target/scala-2.10/ivy-0.0.1.xml
	[trace] Stack trace suppressed: run last *:publish for the full output.
	[error] (*:publish) java.io.IOException: Access to URL http://localhost:8081/nexus/content/repositories/releases/test/thing_2.10/0.0.1/thing_2.10-0.0.1.pom was refused by the server: Unauthorized
	[error] Total time: 0 s, completed Jul 2, 2015 11:56:03 AM

And after looking through a [few](http://stackoverflow.com/questions/16425639/sbt-publish-to-corporate-nexus-repository-unauthorized) [posts](http://blog.restphone.com/2012/10/sbt-pushing-and-pulling-from-local.html) [on](http://stackoverflow.com/questions/4348805/how-can-i-access-a-secured-nexus-with-sbt) [the](https://groups.google.com/forum/?fromgroups=#!topic/simple-build-tool/n0v0jd4UWOQ) [web](http://stackoverflow.com/questions/4348805/how-can-i-access-a-secured-nexus-with-sbt) I finally got my Realm right 
by checking the headers via `curl`. 

	curl -I -XPOST http://localhost:8081/nexus/content/repositories/releases/test/thing_2.10/0.0.1/drupalslick_2.10-0.0.1.pom -v > /dev/null 

During this process I also tried out 

	curl -u admin:admin123 -I -XPOST http://localhost:8081/nexus/content/repositories/releases/test/thing_2.10/0.0.1/drupalslick_2.10-0.0.1.pom -v > /dev/null 

Which returned successful, so I figure'd there wasn't an issue with my setup. However,
a few minutes later of messing with the realm settings and credentials in SBT, I 
started getting a 400 error instead. By this point, I had all my loggers on Nexus 
turned up to maximum and was viewing errors like

	2015-07-02 12:22:35,208-0400 DEBUG [qtp2141807259-51] anonymous org.apache.shiro.web.filter.authc.BasicHttpAuthenticationFilter - Authentication required: sending 401 Authentication challenge response.
	2015-07-02 12:22:51,885-0400 DEBUG [qtp2141807259-54] *UNKNOWN org.apache.shiro.web.filter.authc.BasicHttpAuthenticationFilter - Attempting to execute login with headers [Basic YWRtaW46YWRtaW4xMjM=]

But wasn't seeing the 400. So instead, I turned towards the ever trusty tool: `tcpdump`!
Since I couldn't see the request on the Nexus side, I decided to watch what was happening 
on the SBT side. 

	 sudo tcpdump -i lo0 -n -s 0 -w - 

And hitting `publish` one more time from the SBT CLI immediately got me the answer:

	?!~/?!xHTTP/1.1 400 Bad Request
	Date: Thu, 02 Jul 2015 16:23:05 GMT
	Server: Nexus/2.11.3-01
	X-Frame-Options: SAMEORIGIN
	X-Content-Type-Options: nosniff
	Accept-Ranges: bytes
	Content-Type: text/html
	Transfer-Encoding: chunked

	2EA
	<html>
	  <head>
	    <title>400 - Repository with ID='releases' does not allow updating artifacts.</title>
	    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

	    <link rel="icon" type="image/png" href="http://localhost:8081/nexus/favicon.png">
	    <!--[if IE]>
	    <link rel="SHORTCUT ICON" href="http://localhost:8081/nexus/favicon.ico"/>
	    <![endif]-->

	    <link rel="stylesheet" href="http://localhost:8081/nexus/static/css/Sonatype-content.css?2.11.3-01" type="text/css" media="screen" title="no title" charset="utf-8">
	  </head>
	  <body>
	    <h1>400 - Repository with ID='releases' does not allow updating artifacts.</h1>
	    <p>Repository with ID='releases' does not allow updating artifacts.</p>
	  </body>
	</html>

**Derp!** Of course I was getting a 400, since I wasn't versioning with a Snapshot, the 
deployment policy on Nexus was refusing to change the empty POST request I had sent when 
testing with `curl`. That's an easy fix in nexus though:

<img src="/images/tech-blog/nexus-sbt.png" width="600px">

So let this be a helpful reminder to anyone else: Don't test a repository configuration 
with the release branch! 

[Sonatype's Nexus]:http://www.sonatype.org/nexus/go/
[fantastic documentation]:http://books.sonatype.com/nexus-book/index.html
[installation manual]:http://books.sonatype.com/nexus-book/reference/install.html
[SBT]:http://www.scala-sbt.org/
[specifically on just that]:http://books.sonatype.com/nexus-book/reference/sbt.html