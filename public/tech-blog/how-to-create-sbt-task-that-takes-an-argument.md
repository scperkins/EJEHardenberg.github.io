### How to create a task that takes an argument in sbt

Something that comes up when you're coming to an end of a project is the 
simple question of how to deploy it. For the hobbyist, deploying might be 
as simple as installing libraries or services to a machine and sftp-ing 
the contents of their project up to a server. For a professional, it may 
involve setting up [builds on Jenkin's servers and deploy key's on github], 
then creating a deployed and auto-scaling environment on something like 
Amazon or Rackspace. 

If you're using [SBT] it's natural that to deploy something with a build 
in jenkins you would use something like [SBT Assembly] or [SBT Native Packager]. 
If you're also using the [PlayFramework] you're likely familiar with the 
[dist task] which creates a deployment for your application. No matter what 
you use to create your final application, if you're doing an enterprise 
launch of some kind, you'll likely have more than one environment. A possible 
setup might include:

1. A development environment to test feature branches on
2. An integration environment to ensure features work with each other
3. A production environment that is live.

With those in mind, your build task will likely use different configuration 
files, and so you'll want to change that for each environment. But when 
making an sbt task, how do you do that? It's not too hard if you read 
the [documentation on Input Tasks] and on [Parsers] for a few minutes. 
Here's the long and skinny:

1. Imports go at the **top** of your build.sbt file. 
```
import sbt.complete._
import complete.DefaultParsers._
```
2. Next, define your task as `inputKey` since it takes input:
```
val myTask = inputKey[Unit]("This task takes a parameter!")
```
3. Define the input to your task, in our example let's say we'll have the 
environment as the variable:
```
val stageEnv: Parser[String] = " staging" 
val intEnv : Parser[String] = " integration" 
val prodEnv : Parser[String] = " production"
val combinedParser: Parser[String] = stageEnv | intEnv | prodEnv
```
4. Define what your task is going to do!
```
myTask := {
  val environment = combinedParser.parsed.trim
  val s = streams.value
  s.log.info(s"Parameter was $environment")
}
```
5. If neccesary, have dependent tasks run first. For example, to run `myTask` 
after the `dist` task in play try:
```
myTask <<= myTask.dependsOn(dist in Universal)
```
6. Run `sbt` and `myTask <environment>` where `environment` is staging, 
integration or production.

And that's the step by step process. I find myself learning from simple 
examples like these much better than other ways. The documentation on 
[combining parsers] states you can do things like

	val color: Parser[String] = "blue" | "green"

But I found that sbt complained when doing so. The other thing to notice 
here is that I `trim`ed the output of the parsed environment. Why? Because 
it has an extra space in the parser see? The trick with the regular 
`Parser[String]` is that it takes the literal string. 

This is all I wanted to cover in this blog post, but depending on interest, 
I might write up a small series on going from small examples to bigger 
ones with SBT, or just provide some simple templates or examples of SBT 
usage that I've seen come in handy.

[builds on Jenkin's servers and deploy key's on github]:/tech-blog/jenkins-multiple-deploy-keys-and-github
[SBT]:http://www.scala-sbt.org/
[SBT Assembly]:https://github.com/sbt/sbt-assembly
[SBT Native Packager]:https://github.com/sbt/sbt-native-packager
[PlayFramework]:https://www.playframework.com
[dist task]:https://www.playframework.com/documentation/2.3.x/ProductionDist
[documentation on SBT]:http://www.scala-sbt.org/release/docs/Input-Tasks.html
[Parsers]:http://www.scala-sbt.org/release/docs/Parsing-Input.html
[combining parsers]:http://www.scala-sbt.org/release/docs/Parsing-Input.html#Combining+parsers