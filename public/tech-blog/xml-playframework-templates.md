### XML PlayFramework Templates

While [some people hate Scala's XML], I haven't worked with it long enough 
to form an opinion. So today I decided that I'd dive into it by creating 
an application that wrapped some simple data and spat out some XML.

Since I'm mainly focusing on the XML side of things, I'd rather not deal 
with connecting to database's or anything like that. So our data will come 
from a simple [companion object] instead of a database. 

** Tip: ** If you'd like to follow along in the code or make modifications yourself, 
simply clone the [example repository here].

First off, we need to create the project structure:

	mkdir app
	mkdir app/controllers
	mkdir app/views
	mkdir app/models
	mkdir conf
	touch conf/routes
	mkdir project
	touch project/plugins.sbt
	touch build.sbt

Next, setup the build file to name your project and enable the Play Plugin:

	//build.sbt

	lazy val root = (project in file(".")).enablePlugins(PlayScala)
	
	name := "xml-example"
	
	version := "1.0"
	
	scalaVersion := "2.10.4"

In order for this to load when we run `sbt`, we need to specify where the 
PlayPlugin is coming from by editing the **project/plugins.sbt** file:

	// The Typesafe repository
	resolvers += "Typesafe repository" at "https://repo.typesafe.com/typesafe/releases/"
	
	// Use the Play sbt plugin for Play projects
	addSbtPlugin("com.typesafe.play" % "sbt-plugin" % "2.3.8")

With that in place we can now run `sbt` and get a pleasant error message 
from play about having no routes setup. To remedy update your routes file:

	GET / controllers.Example.index

In order for this to compile we need to have an `Example` controller. So 
create one of those in **controllers/Example.scala**:


	package controllers
	
	import play.api._
	import play.api.mvc._
	
	object Example extends Controller {
	
	  def index = Action {
	    Ok(views.xml.index(models.TestInfo.getData))
	  }
	
	}

Now we'll get an error about the views file not being defined, and the 
models not being defined either. Let's create the models file first:


	package models
	
	import play.api._
	import play.api.mvc._
	
	case class TestInfo(id: Int, name: String, days: List[String])
	
	object TestInfo {
	  def getData : List[TestInfo] = {
	    List(
	      TestInfo(1, "First", List("Monday","Tuesday")),
	      TestInfo(2, "First", List("Wednesday","Thursday")),
	      TestInfo(3, "First", List("Monday","Friday")),
	      TestInfo(4, "First", List("Saturday","Sunday")),
	      TestInfo(5, "First", List()),
	      TestInfo(6, "First", List("Tuesday"))
	    )
	  }
	}

We've defined the [companion object] that will provide us with test data, 
and a simple [case class] to make doing so easier. Normally we'd write up 
something here that would provide data from a backend, such as [elastic 
search] or [MySQL], but today it's just test data. Using this model we 
can now write our **app/views/index.scala.xml** file:


	@(nodeList : List[TestInfo])
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList>
	    @for(testInfo <- nodeList){
	    <TestInfo>
	        <Id>@testInfo.id</Id>
	        <Name>@testInfo.name</Name>
	        <Days>
	            @for(day <- testInfo.days){
	            <Day>@day</Day>
	            }
	        </Days>
	    </TestInfo>
	    } 
	</TestInfoList>

You'll notice there isn't anything different about this file versus a regular
xml template except that the name of the file is **index.scala.xml** as oppose 
to your usual **index.scala.html**. However, to illustrate a point, let's 
refactor our view to abstract the `TestInfo` view to it's own file:

	mkdir app/views/common
	vi app/views/common/testinfo.scala.xml

	@(testInfo: models.TestInfo)
	<TestInfo>
	    <Id>@testInfo.id</Id>
	    <Name>@testInfo.name</Name>
	    <Days>
	        @for(day <- testInfo.days){
	        <Day>@day</Day>
	        }   
	    </Days>
	</TestInfo>

With this in place we'll change the **app/views/index.scala.xml** file to 
call the new one:

	@(nodeList : List[TestInfo])
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList>
	    @for(testInfo <- nodeList){
	    	@common.testinfo(testInfo)
	    } 
	</TestInfoList>

Note that the directories under the **views** folder correspond to their 
packages. For those in the root of views, their type (html,xml) will be the 
package (look at the controller, see `views.xml.index`?). For templates in 
the subdirectories, the classes become views.&lt;subdir&gt;.fileName.

XML is a useful protocol, but in order to have standards between the producer 
and consumer we need to specify a schema file, or an XSL. These are pretty easy 
to understand just by reading them, here's **public/testInfo.xsd**:

	<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>
	  <xs:element name="TestInfoList">
	    <xs:complexType>
	      <xs:sequence>
	        <xs:element ref="TestInfo" minOccurs='0' maxOccurs='unbounded'/>
	      </xs:sequence>
	    </xs:complexType>
	  </xs:element>

	  <xs:element name="TestInfo">
	    <xs:complexType>
	      <xs:sequence>
	        <xs:element ref="Id" minOccurs='1' maxOccurs='1'/>
	        <xs:element ref="Name" minOccurs='1' maxOccurs='1'/>
	        <xs:element ref="Days" minOccurs='1' maxOccurs='1'/>
	      </xs:sequence>
	    </xs:complexType>
	  </xs:element>

	  <xs:element name="Name" type='xs:string'/>
	  <xs:element name="Id" type='xs:integer'/>
	  <xs:element name="Days">
	    <xs:complexType>
	      <xs:sequence>
	        <xs:element ref="Day" minOccurs='0' maxOccurs='7'/>
	      </xs:sequence>
	    </xs:complexType>
	  </xs:element>

	  <xs:element name="Day" type='xs:string'/>
	</xs:schema>

This file says that the valid scheme is one which has a `TestInfoList` node 
that contains any number of `TestInfo` elements. Each of these elements are 
then defined in terms of their pieces, namely `Id`, `Name`, and `Days`. As 
you might expect, each of these elements are defined within the file. XSD 
is [powerful], being Turing complete, we could techically accomplish almost 
anything in it we could do in other languages! However, for this post we're 
just going to use it to validate our generated XML. Let's update the output 
of our layout:

	
	@(nodeList : List[TestInfo])
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList 
	    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	    xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd"
	>
	    @for(testInfo <- nodeList){
	        @common.testinfo(testInfo)
	    }
	</TestInfoList>

I'm assuming that you're running play on the default server port of 9000 
in the example above. To make the `/testInfo.xsd` route work we need to 
update the routes themselves in **conf/routes**: 

	GET /				controllers.Example.index
	GET /testInfo.xsd 	controllers.Assets.at(path:String = "/public/", file:String = "testInfo.xsd")

With those two things in place, any client will be able to validate your 
xml using the provided schema. If you want to check it out yourself, try 
this on the command line:

	curl http://localhost:9000/ > tmp.xml
	xmllint --schema public/testInfo.xsd tmp.xml

And you should see a success method.

This post went over the bare neccesities of getting a Play application up 
from scratch and serving validatable XML. By using templates for pieces 
of your XML you can modularize your view code and make your life easier 
later on. Hopefully after reading this post you realize how easy it is 
to create XML views with Play. Have fun and happy coding!

[some people hate Scala's XML]:http://anti-xml.org/
[companion object]:http://tutorials.jenkov.com/scala/singleton-and-companion-objects.html
[example repository here]:https://github.com/EdgeCaseBerg/scala-xml-example
[case class]:http://www.scala-lang.org/old/node/107
[elastic search]:https://www.elastic.co
[MySQL]:http://alvinalexander.com/scala/scala-jdbc-connection-mysql-sql-select-example
[powerful]:https://en.wikipedia.org/wiki/XSLT