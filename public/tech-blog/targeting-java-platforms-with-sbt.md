### How to target JVM environments in Play! Framework (scala) with SBT

Unfortunately, legacy systems exist. Many times these systems run on old
or antiquated hardware, sometimes the applications are so tightly wound
to the environment that a component can't be upgraded unless you upgrade
100 others. More than that, on some occasions, environments can differ
in ways like: staging, qa, production, NEW production with shiny new
tools, NEW NEW production, NEW staging, etc etc.

Unless one is careful and thorough in their system administration, a
local environment can often differ from live ones. For example, if your
JVM and java version are different then some web server you inherited
from a 15 year old legacy project. 

Luckily, when you compile java files with `javac` you can specify both
the `-source` and `-target` version. And for people using [sbt] there's
a simple way to specify these from your build.sbt file. 

	javacOptions ++= Seq("-source", 1.7, "-target", 1.7)
	scalacOptions := Seq(-target:jvm-1.7)

Of course, this doesn't do you much good if you're using version
control, as you'll end up needing to commit different versions whenever
you try to build unless your deploy process specifies that information.
So instead of hard coding the java version, it's better to use a
variable you can set on starting your sbt process. To do this, we need
to pull in environmental variables to our build.sbt. How do we do this?
Simple, we use [sys.props.getOrElse]! 


	val javaTargetVersion = sys.props.getOrElse("JAVATARGET", default = "1.7") 
	javacOptions ++= Seq("-source", javaTargetVersion, "-target", javaTargetVersion)
	scalacOptions := Seq(s"-target:jvm-$javaTargetVersion")

With this in our build file we can now use `-D` variables when starting
sbt to define which version of java we'll target. For example: 

	sbt -DJAVATARGET=1.6 clean compile dist

Will build and package a zip file for our application targeting a system
using java 1.6. 

We can stop here, but most people don't want to remember or type out a
long list of `-D` variables. Rather, most people would at most type out
a single switch to their build. Something like 

	sbt -DENV=stage clean compile dist

So how do we support that? One would think it would be simple, use
something like this:

	val env = sys.props.getOrElse("ENV", default = "local") 
	
	val (javaTargetVersion, sourceVersion, jvmVersion) = env match {
		case "local" => ("1.7","1.7","1.7")
		case "stage" => ("1.6","1.7","1.6")
		case "production" => ("1.7","1.7","1.8")
	}

_But you'd be wrong_. If you attempt to do this you'll get an error from
the compiler that says: 

	[error]  Pattern matching in val statements is not supported

As of right now, even defining a function in Build.scala doesn't work to
resolve the error message and allow for something like the above. There
may be a way to do it, but as of this writing, <strike>I'm still waiting for an
answer to my [StackOverFlow Question]. 

Until the scala community responds, we'll be stuck specifying -D flags
to sbt in bulk. But even with the slight inconvenience, it's not so bad,
as we could automate such things with makefiles.</strike>

** Update ** 

As stated by [Gabriele Petronella] in the answer to my [StackOverFlow
Question] the SBT parser does not support assigning to tuples. But, if
you use a [case class] then you'll be ok. This needs to be done in the
Build.scala file like so: 

	import sbt._
	import Keys._
	
	case class EnvData(target: String, source: String, jvm: String)

And then you can update the build.sbt file to use this new class to have
a more informative and clear process:

	
	val env = sys.props.getOrElse("ENV", default = "local") 
	
	val envData = env match {
		case "local" => EnvData("1.7","1.7","1.7")
		case "stage" => EnvData("1.6","1.7","1.6")
		case "production" => EnvData("1.7","1.7","1.8")
	}
	
	val targetJvm = s"-target:jvm-${envData.jvm}" 
	
	scalacOptions := Seq(
	  "-unchecked",
	  "-deprecation",
	  "-feature",
	  "-encoding", "utf8",
	  targetJvm
	)
	
	javacOptions ++= Seq("-source", envData.source, "-target", envData.target)



If you'd like to see an example Play Application using the sbt setup
described above, check out this [example repository].


[sbt]:http://www.scala-sbt.org/release/tutorial/Directories.html
[sys.props.getOrElse]:http://www.scala-lang.org/api/current/index.html#scala.sys.SystemProperties
[StackOverFlow Question]:https://stackoverflow.com/questions/29864732/is-there-a-way-to-use-pattern-matching-in-build-sbt
[example repository]:https://github.com/EdgeCaseBerg/sbt-target-example
[Gabriele Petronella]:https://stackoverflow.com/users/846273/gabriele-petronella
[case class]:http://www.scala-lang.org/old/node/107
