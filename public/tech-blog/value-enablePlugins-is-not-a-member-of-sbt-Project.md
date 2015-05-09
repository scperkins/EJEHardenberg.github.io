### value enablePlugins is not a member of sbt.Project 

Today I was setting up a couple of projects. One was a simple model library, the 
next an [Akka] application, and the last a [Play] app that started spitting up 
errors after I had finished setting up the initial project structure. 

	[info] Loading project definition from /path/project
	[info] Compiling 1 Scala source to /path/project/target/scala-2.10/sbt-0.13/classes...
	[error] bad symbolic reference. A signature in Play.class refers to type AutoPlugin
	[error] in package sbt which is not available.
	[error] It may be completely missing from the current classpath, or the version on
	[error] the classpath might be incompatible with the version used when compiling Play.class.
	[error] /path/project/Build.scala:21: value enablePlugins is not a member of sbt.Project
	[error] possible cause: maybe a semicolon is missing before `value enablePlugins'?
	[error]     .enablePlugins(play.PlayScala)
	[error]      ^
	[error] two errors found
	[error] (compile:compile) Compilation failed
	Project loading failed: (r)etry, (q)uit, (l)ast, or (i)gnore? q

I did a little searching only but couldn't find anything that seemed to match my 
case. After meticulously comparing the few files in the project to the examples 
on in the documentation, I found the [upgrade guide], and noticed that the sbt 
version was different than what my build.properties file stated.

So I opened up build.properties and noted the version I originally had

	sbt-version=0.13.0

and replaced it with the one in the migration docs:

	sbt.version=0.13.5 

Hopefully this helps anyone else running into similar issues. 


[Akka]:http://akka.io/
[Play]:https://www.playframework.com
[upgrade guide]:https://www.playframework.com/documentation/2.3.x/Migration23