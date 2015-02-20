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

When you have a large number of projects, it also helps to organize 
dependencies. [There's good documentation on how to make reusable dependencies] 
that I won't bother repeating here.


#### Getting to some code

Now that we have an idea of how to organize our code and projects, let's 
actually get to some code. If you run the scala console, or sbt's console 
command you'll drop into a shell that can be used to test out some 
expressions:

	Welcome to Scala version 2.10.4 (OpenJDK 64-Bit Server VM, Java 1.7.0_55).
	Type in expressions to have them evaluated.
	Type :help for more information.

	scala> 1 + 2
	res0: Int = 3
	
	scala> res0 + 4
	res1: Int = 7
	
	scala> 

One of the nice things about the scala console that I haven't seen before 
is the `res0` `res1` variables that are auto populated when you do 
computations. Which you can then use. You'll find your typical primitive 
types in scala, `Int`'s, `Boolean`'s, `Double`'s, and `String` to name a 
few. 

In addition, you can also define anonymous functions, similar to 
javascript. This is helpful when you're testing things out in the shell 
and don't want to write a full blown class and compile to test things. 

	scala> val f = (x: Int) => { x + 2 }
	f: Int => Int = <function1>
	
	scala> f(3)
	res12: Int = 5

And here we burst into a few things. 

1. `val` to define a value, AKA, something which doesn't change. 
2. `(x: Int)` the way to define arguments and their types in a function definition 
3. ` => ` seperates signature from the anonymous function body
4. `{ ... }` how to define the body of an anonymous function

And of course calling the function is exactly what'd you find in any other 
language `f(argument)`. Well, sometimes, Let's take a look at a bit of a 
weird call:

	scala> (1 to 5).toList.foldLeft(0)((a: Int, b) => { a + b})
	res9: Int = 15

Saying `(1 to 5).toList) is the same as saying `List(1,2,3,4,5)` but it's 
a bit less wordy and more flexible. `foldLeft` is a concept that is likely 
familiar to people who have been introduced to functional programming before. 
Folding is when you aply an operation across an iterable and accumulate the 
results. `foldLeft` is a function, but it takes **two** sets of parenthesis. 
Seem weird? Well, it's syntactic sugaring for being able to pass an anonymous 
function as an argument to the `foldLeft` function. It could also be written 
as ` (1 to 5).toList.foldLeft(0) { (a: Int, b) => a + b }`. 

One of the strengths of functional programming is matching. This is similar 
to switch statements but much much more powerful. Here's a toy example:

	val g = (n: AnyVal) => { 
		n match { 
			case i:Int => println("int")
			case d:Double => println("double")
			case _ => println("lol wut")
		} 
	}

	g(1) //-> int
	g(2.0) //-> double
	g("hi") //-> lol wut

This function can literally handle any type of input, if it doesn't know 
how to handle it, it will print the obligatory "lol wut" and end. When 
applied to more complex scenarios this can provide simple ways to branch 
a program based on inputs. If you really wanted to, you could probably 
avoid if statements to some degree since they're the same as something 
like this:

	2 < 4 match { case true => 1; case false => 2 }

Though why you'd want to do this I'm not sure quite yet, esoteric reasons 
perhaps. 

A more realistic example is dealing with XML files. While most of the 
web world is __slowly__ moving to JSON. Much of it still exists within 
XML. Which is fine as far as scala is concerned because it provides a 
degree of native support for it. In the scala interpretter you can 
write out XML freely and then do some basic [xpath] querying on it.

Let's say we have a configuration file that looks something like this:

	<config>
		<database environment="local">
			<password>foo</password>
			<username>bar</username>
			<name>baz</name>
			<host>boz</host>
		</database>
		<database environment="dev">
			<password>foo2</password>
			<username>bar2</username>
			<name>baz2</name>
			<host>boz2</host>
		</database>
		<database environment="production">
			<password>foo3</password>
			<username>bar3</username>
			<name>baz3</name>
			<host>boz3</host>
		</database>
	</config>

Then in scala we can either have this be a variable like so: 

	val conf = <config><database //omitting the rest but you get the idea
	//or load it using the XML library:
	scala.xml.XML.loadFile("conf.xml")

We can then grab all the database nodes via xpath: `conf \\ "database"` 
which will give us a `NodeSeq` type back. Which we can filter on the 
environmental attribute with `.filter`. here's an example: 


	scala> var datasource = (conf \\ "database").filter(dNode => dNode.attribute("environment").exists(env => env.text == "dev"))
	datasource: scala.xml.NodeSeq = 
	NodeSeq(<database environment="dev">
				<password>foo2</password>
				<username>bar2</username>
				<name>baz2</name>
				<host>boz2</host>
			</database>)
	(datasource \ "host").text // gives back boz2

It's pretty easy to see how this could then be used to easily parse out and use 
for custom configuratons of your own system.

Overall, so far what I've seen of scala is interesting. The syntax is enjoyable 
and the community seems interesting and intelligent. I've picked up some books 
and plan on creating a few projects using scala soon. This post has gotten a bit 
long and didn't have much of a point but to chronologue some of the things I was 
playing with. So perhaps this will inspire you to pick up scala! A really good 
post to read if you're interested in learning more is [this one], good luck!


[sbt's website]:http://www.scala-sbt.org/release/tutorial/Basic-Def.html
[file]:http://www.scala-sbt.org/0.12.1/sxr/Keys.scala.html#324085
[files to be cleaned]:http://www.scala-sbt.org/release/tutorial/More-About-Settings.html
[There's good documentation on how to make reusable dependencies]:http://www.scala-sbt.org/release/tutorial/Organizing-Build.html
[xpath]:https://en.wikipedia.org/wiki/XPath
[this one]:http://www.vasinov.com/blog/16-months-of-functional-programming/