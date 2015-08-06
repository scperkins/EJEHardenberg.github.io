### Logging to a File with Spray

Whenever something goes wrong, you're going to be happy to have a logfile
that helps debug the issue. Logging is so important that people do benchmarks 
on the [performance of writing to logs and offer tweaking advice]. Let's talk 
about the simplest performance boost you can add to your application. 

#### The [AsyncAppender]

Imagine you've writing some really nice code in [Spray], the dispatchers are 
running, the threads are firing short and sweet. Everything is asynchronous. 
You're good right? Well, maybe not if you're using a synchronous [FileAppender]. 
What happens when the logging you've been so dilligent about adding to your a
application fires from each of your 100 threads and tries to write to 1 resource?

Blocking and slowing that's what happens. So we need to fix that by making your 
logging be just as performant as the rest of your code. We can do that by taking 
your old logback configuration and updating it with something else. For example, 
let's assume you've got your application setup like this:

	app/
		project/
		src/
			main/
				resources/
					logback.xml
					application.conf
				scala/

And a simple logback file you've copied from the bowels of documentation or StackOverflow:

	<?xml version="1.0" encoding="UTF-8"?>
	<configuration scan="false" debug="false">
	  <appender name="CONSOLELOG" class="ch.qos.logback.core.ConsoleAppender">
	    <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
	      <Pattern>
	        %d{yyyy-MM-dd HH:mm:ss} %-5level - %msg%n
	      </Pattern>
	    </encoder>
	  </appender>
	  <appender name="FILELOG" class="ch.qos.logback.core.FileAppender">
	    <File>log/app.log</File>
	    <param name="Append" value="true" />
	    <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
	      <Pattern>
	        %d{yyyy-MM-dd HH:mm:ss} %-5level - %msg%n
	      </Pattern>
	    </encoder>
	  </appender>

	  <root level="INFO">
	    <priority value="debug" />
	    <appender-ref ref="FILELOG"/>
	    <appender-ref ref="CONSOLELOG"/>
	  </root>
	</configuration>

You're pretty happy with this since it creates a log file and writes out to it, 
as well as writing out to the console for your IDE or Console to see during your 
development. But you've read the blogs and the documentation and you've decided 
the first thing you want to do is get one of those fancy AsyncAppenders. So you 
add in the Async as a proxy:


	  <!-- The other appenders ... -->
	  <appender name="async" class="ch.qos.logback.classic.AsyncAppender">    
	    <queueSize>500</queueSize>
	    <appender-ref ref="CONSOLELOG"/>
	    <appender-ref ref="FILELOG"/>
	    <includeCallerData>true</includeCallerData>
	  </appender>
	  <!-- The root ... -->

Great you think! And you boot up your application, excited and ready for your 
logfile to show everything quickly without slowing down your application! And 
then. _Nothing_. But wait why? Setting the `debug` attribute on your configuration
element, you quickly spot an error message:

	myapp 17:01:53,513 |-INFO in ch.qos.logback.classic.AsyncAppender[async] - Attaching appender named [CONSOLELOG] to AsyncAppender.
	myapp 17:01:53,513 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [FILELOG] to ch.qos.logback.classic.AsyncAppender[async]
	myapp 17:01:53,514 |-WARN in ch.qos.logback.classic.AsyncAppender[async] - One and only one appender may be attached to AsyncAppender.
	myapp 17:01:53,514 |-WARN in ch.qos.logback.classic.AsyncAppender[async] - Ignoring additional appender named [FILELOG]

Outraged, you storm off and destroy a city like Godzilla. How dare the appender 
have such a constraint! Well, there are [reasons for it listed in logback's Jira]

>As for attaching multiple appenders, given the lossy nature of AsyncAppender, it would be "dangerous" to attach multiple appenders to a given AsyncAppender instance because a slow appender would affect the events sent to the other presumably faster appenders attached to said AsyncAppender instance.

In other words, let's say you had 3 appenders that the AsyncAppender was supposed to 
write to. Within the [source code] you'll notice that the internal queue is a 
blocking one. And that at some point we'll loop over the appenders and put the 
event onto them. If one of these appenders was slow, then they'd slow down the 
other appenders. And, as noted in the [AsyncAppender] documentation:

>In order to optimize performance this appender deems events of level TRACE, DEBUG and INFO as discardable.

And in the [online docs]

>LOSSY BY DEFAULT IF 80% FULL AsyncAppender buffers events in a BlockingQueue. A worker thread created by AsyncAppender takes events from the head of the queue, and dispatches them to the single appender attached to AsyncAppender. Note that by default, AsyncAppender will drop events of level TRACE, DEBUG and INFO if its queue is 80% full. This strategy has an amazingly favorable effect on performance at the cost of event loss.

So if our appenders were slow, and the Queue started filling up due to some of 
the appenders slowing down, we'd start losing messages (unless you configure it 
otherwise).

So to put down our logging our configuration file might look like this:

	<?xml version="1.0" encoding="UTF-8"?>
	<configuration scan="false" debug="false">
	  <appender name="CONSOLELOG" class="ch.qos.logback.core.ConsoleAppender">
	    <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
	      <Pattern>
	        %d{yyyy-MM-dd HH:mm:ss} %-5level - %msg%n
	      </Pattern>
	    </encoder>
	  </appender>
	  <appender name="FILELOG" class="ch.qos.logback.core.FileAppender">
	    <File>log/ica.log</File>
	    <param name="Append" value="true" />
	    <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
	      <Pattern>
	        %d{yyyy-MM-dd HH:mm:ss} %-5level - %msg%n
	      </Pattern>
	    </encoder>
	  </appender>
	  <appender name="async1" class="ch.qos.logback.classic.AsyncAppender">    
	    <queueSize>500</queueSize>
	    <appender-ref ref="FILELOG"/>
	    <includeCallerData>true</includeCallerData><!-- Remove for performance if desired -->
	  </appender>
	  <appender name="async2" class="ch.qos.logback.classic.AsyncAppender">    
	    <queueSize>500</queueSize>
	    <appender-ref ref="CONSOLELOG"/>
	  </appender>

	  <root level="INFO">
	    <appender-ref ref="async1"/>
	    <appender-ref ref="async2"/>
	  </root>
	</configuration>

Adding this logback.xml file to your spray application will give you the 
logging your asynchronous program deserves! But... we're not done yet. Spray 
uses [Akka] under the hood (if you're using spray can)

And of course you should configure your [Akka logging] as well in application.conf:

	akka {
		logger-startup-timeout = 5s
		log-dead-letters-during-shutdown = off
		loglevel = "INFO"
	}

Note that this will use the default logger in Akka. Which, as the documentation states
you should not use it for production:

>The default one logs to STDOUT and is registered by default. It is not intended to be used for production. 

So let's use the one implementation they do provide besides the default, [SL4J]. 
Setting this up in our application.conf is pretty easy:

	akka {
		logger-startup-timeout = 5s
		log-dead-letters-during-shutdown = off
		loglevel = "INFO"
		loggers = ["akka.event.slf4j.Slf4jLogger"]
		logging-filter = "akka.event.slf4j.Slf4jLoggingFilter"
	}

Doing this without updating your build.sbt file will result in an error though:

	myapp [ERROR] akka.ConfigurationException: Logger specified in config can't be loaded [akka.event.slf4j.Slf4jLogger] due to [java.lang.ClassNotFoundException: akka.event.slf4j.Slf4jLogger]
	...
	myapp [ERROR] akka.ConfigurationException: Could not start logger due to [akka.ConfigurationException: Logger specified in config can't be loaded [akka.event.slf4j.Slf4jLogger] due to [java.lang.ClassNotFoundException: akka.event.slf4j.Slf4jLogger]]

To provide the class, you need to have two jars in your build.sbt:

	libraryDependencies ++= { 
		Seq(
		...
		"com.typesafe.akka"   %%  "akka-slf4j"  % 2.3.9,
		"org.slf4j" % "slf4j-api" % "1.7.7",
		...
		)
	}

And then you also need to add a logging implementation, like logback:

	"ch.qos.logback"  %  "logback-classic"   % "1.1.3",

Once you have these jars in place you'll be ready for the races! With 
a non-default logger for your Akka system, your AsyncAppender for handling
the actual logging, and your application up and running. You'll be debugging 
all the log files in no time!

[performance of writing to logs and offer tweaking advice]:http://blog.takipi.com/how-to-instantly-improve-your-java-logging-with-7-logback-tweaks/
[AsyncAppender]:http://logback.qos.ch/apidocs/ch/qos/logback/classic/AsyncAppender.html
[Spray]:http://spray.io
[FileAppender]:http://logback.qos.ch/apidocs/ch/qos/logback/core/FileAppender.html
[reasons for it listed in logback's Jira]:http://jira.qos.ch/browse/LOGBACK-841
[deadlocked]:https://bz.apache.org/bugzilla/show_bug.cgi?id=41214
[source code]:http://grepcode.com/file/repo1.maven.org/maven2/ch.qos.logback/logback-core/1.0.5/ch/qos/logback/core/AsyncAppenderBase.java#AsyncAppenderBase.addAppender%28ch.qos.logback.core.Appender%29
[online docs]:http://logback.qos.ch/manual/appenders.html#AsyncAppender
[Akka logging]:http://doc.akka.io/docs/akka/snapshot/java/logging.html
[Akka]:http://akka.io/
[SL4J]:http://www.slf4j.org/
