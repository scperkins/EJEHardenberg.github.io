### Scala 101 - My first look

I'm currently transitioning from Java to Scala and learning more about 
functional programming. While I have done functional programming before, 
it was, sadly, several years ago so refreshing my memory is the first 
priority here. 

There's a lot on the net about scala, but I decided to get started with 
sbt. I know this may sound weird, not doing a language tutorial and 
immediately jumping to a build tool. But I like preparing myself for 
development environments first before I dive into learning details of a 
language. Afterall, most of the time as a dev you're playing plumber and 
glueing different libraries together, so it makes sense to start out 
learning how to do that.  

#### Defining library dependencies

Here's an example of library dependencies and setup from [sbt's website]

	val derby = "org.apache.derby" % "derby" % "10.4.1.3"

	lazy val commonSettings = Seq(
	  organization := "com.example",
	  version := "0.1.0",
	  scalaVersion := "2.11.4"
	)

	lazy val root = (project in file(".")).
	  settings(commonSettings: _*).
	  settings(
	    name := "hello",
	    libraryDependencies += derby
	  )

The `_*` allows the sequence to be passed to the settings method.

The points of note here is that the `commonSettings` is where you'd 
define your project's package details and versions. Then for each of the 
components of your project you'd define the name's and their libraries. 
If you're doing something with custom libraries and are defining a single 
application you'd likely have something like this:

	name := "Project Name"

	version := "0.0.1"

	scalaVersion := "2.11.1"

	resolvers += "Repo Name" at "http://urltotherepository"

	libraryDependencies += "com.example" % "artifact" % "1.0.0"

	libraryDependencies += "com.example" % "artifact2" % "1.0.0"

	etc...

#### Tasks and inspection

An interesting thing about sbt's shell is that you have the ability to 
`inspect` any task you could run. For example, if you define the example 
task from the documentation: 

	lazy val hello = taskKey[Unit]("An example task")
	lazy val root = (project in file("."))
   		.settings(commonSettings:_*)
   		.settings(
   			name := "hello",
         	version := "1.0",
         	hello := {
             	println("Hello!")
       		}
		)

And the run `inspect hello` you'll see useful information like so: 

	> inspect hello
	[info] Task: Unit
	[info] Description:
	[info] 	An example task
	[info] Provided by:
	[info] 	{file:/path/to/example/hello/}root/*:hello
	[info] Defined at:
	[info] 	/path/to/example/hello/build.sbt:14
	[info] Delegates:
	[info] 	*:hello
	[info] 	{.}/*:hello
	[info] 	*/*:hello

Which tells you where you can find the definition of the task. Handy if 
you're wondering what the task does and you didn't write it yourself. 
If you look at the `compile` task you can see that it's defined in the 
`(sbt.Defaults) Defaults.scala:250` [file]. I can imagine this being 
helpful for contributing or patching other projects or frameworks.

#### Deleting custom files with clean

The other handy thing I found in the documentation was the ability to 
add [files to be cleaned] via `cleanFiles` in *build.sbt* like so:

	cleanFiles += file("/tmp/data.txt")

Then when you run `clean` that file will be removed. I can see this 
being handy for when your code generates reports of some kind. Another 
handy thing, is that if your program code has more than one class 
defining the `main` function for some reason when you run `run` from the 
sbt shell it will ask you which you'd like to run. My first thought when 
I saw this it made me think of writing scala deployment/management scripts 
to manage or run jobs from a shell. 

#### Scala versions and sbt's 'dumbness'

An interesting thing about scala is that the jars are expected to have 
the version of scala within their name. If you follow the examples on 
sbt's page and run `package` you'll end up with: **hello_2.10-1.0.jar** 
in target directory. 

When specifying dependencies you'll run into two flavors: 

	libraryDependencies += "org.scala-tools" % "scala-stm_2.11.1" % "0.3"

or 

	libraryDependencies += "org.scala-tools" %% "scala-stm" % "0.3"

The `%%` will implicitly assume that the version of scala specified for 
your project is the one it should use in the artifact's name. So if you
need to use a jar that differs from your own scala language version 
you'll need to use a single `%` and specify.

#### Organization of large projects

If you were creating a larger project in java you might use modules in 
maven to create the project. In scala, there is a similar way of doing 
this. **Aggregates**. Here's an example from me fooling around with scala:

_build.sbt_

	lazy val helloTask = taskKey[Unit]("An example task") 
	lazy val multiTask = taskKey[Unit]("An example task showing aggregates") 
	
	lazy val commonSettings = Seq(
		organization := "com.example",
		scalaVersion := "2.10.4",
		version := "0.1.0"
	)
	
	lazy val hello = (project in file("hello"))
		.settings(commonSettings:_*)
		.settings(
			name := "hello",
			version := "1.0",
			helloTask := { 
				println("Hello!") 
			}
		)
	
	lazy val util = (project in file("util"))
		.settings(commonSettings:_*)
		.settings(
			name := "util",
			version := "1.0"
		)
	
	lazy val multi = (project in file("."))
		.aggregate(util, hello)
		.dependsOn(util)
	
	cleanFiles += file("/tmp/data.txt")

_./Go.scala_

	package com.example
	
	object Go {
		def main(args: Array[String]): Unit = {
		 	println("Running Aggregate!")
			val e = new Example();
			e.sayHello()
		}
	}

_./util/src/main/java/com/dealer/Example.java_

	package com.example;
	
	public class Example {
		public void sayHello(){
			System.out.println("Hey there!");
		}
	}

_./hello/src/main/scala/hw.scala

	object Hi {
  		def main(args: Array[String]) = println("Hi!")
	}

 
There's a three projects going on here. The **hello** project, the 
**util** project, and the **multi** project. When you run sbt in the 
root directory, you'll compile all projects and then `run` the _go_ 
script. If you run sbt in the hello directory, you'll only compile 
the hello files and `run` will give you the "Hi!" string. 

If you `package` from the root, you'll end up with 3 jars. The real use 
of this would be creating something like this:

	models/
		... source code for shared models
	jobs/ 
		... jobs to be ran etc depends on models
	api/
		... web facing API exposing models 
	site/
		... static website that consumes api and creates jobs

And you'd probably package the whole thing up to deploy it to one server 
(if that was the case). Pretty simple right? In the _build.sbt_ example 
above you'll notice that the multi project aggregates 2 projects but only 
depends on one. An important note here is that multi cannot use anything 
in the hello project. Why? Because it doesn't depend on it, and aggregate 
just means we're going to compile/package all these things at once, not 
that they depend on each other. That's what dependOn is for.


#### Getting to some code

...






[sbt's website]:http://www.scala-sbt.org/release/tutorial/Basic-Def.html
[file]:http://www.scala-sbt.org/0.12.1/sxr/Keys.scala.html#324085
[files to be cleaned]:http://www.scala-sbt.org/release/tutorial/More-About-Settings.html