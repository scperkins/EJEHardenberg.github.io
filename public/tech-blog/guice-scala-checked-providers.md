### Guice Scala & CheckedProviders

**Note:**
_If you're unfamiliar with guice, I highly recommend reading the 
[getting started] or the [motivation] before continuing so you have the 
basic concepts of the library down._

#### Getting the CheckedProviders library in scope

Last night I was working on one of my side projects and after reading 
through the [guice wiki] decided that I should use the `CheckedProvides`
in order to be responsible about my exceptions. Namely, this section of 
the `@Provides` documentation caught my eye:

>Guice does not allow exceptions to be thrown from Providers. Exceptions thrown by `@Provides` methods will be wrapped in a ProvisionException. It is bad practice to allow any kind of exception to be thrown -- runtime or checked -- from an `@Provides` method. If you need to throw an exception for some reason, you may want to use the ThrowingProviders extension `@CheckedProvides` methods.

This particular piece of code involved loading some configuration using 
[typesafe's config library]. Since loading a .conf file can throw any 
of the [ConfigException subclasses], I figure'd that if I had code that 
was providing an instance and possibly throwing an exception that I 
should try to handle it as gracefully as I can. The first thing I had to 
figure out was why I kept getting the annoying dependency exception:

	object throwingproviders is not a member of package com.google.inject

Nothing on the [guice wiki] indicates that you ever need to do anything 
more than include the core library. And not looking at the package level
documentation on the [JavaDoc] at first made me think that of course I 
should have the `throwingproviders` in scope by including the library! 
It's in the docs after all! But, after slowing down and reading a little
more carefully I noticed the one line note on the [extension's JavaDoc]
that I wished I had seen 5 minutes ago

>this extension requires guice-throwingproviders.jar.

So after a quick trip over to maven central [I found what I needed] and
then updated my build.sbt file to include the neccesary dependencies:

	libraryDependencies ++= Seq(
		...
		"com.google.inject" % "guice" % "4.1.0",
		"com.google.inject.extensions" % "guice-throwingproviders" % "4.1.0",
		...
	)

<small>_Note that you can use anything 3.0+, I just used the latest version_</small>

With that I was able to successfully import what I needed within my script:

	import com.google.inject.AbstractModule
	import com.google.inject.throwingproviders.{ CheckedProvides, CheckedProvider }
	import com.typesafe.config.{ ConfigException, ConfigFactory } 

#### The use case & motivation for using CheckedProvider

Now that I had the library imported, I could actually start using it! As 
an example, let's say we're loading up some type of data source 
configuration. So we have a URL where we're getting the data from and an 
access code. A scala model for this might look like:

	import java.net.URL
	case class DataSourceParams(val url: URL, @transient val accessCode)

And let's also say that once we've loaded our local configuration, that 
we're then loading the configured parameters to our application for use. 
So, let's have another model that represents the data we'll load from 
the outside world:

	case class RemotePizzaOrder(
		val numberOfPizzas: Long,
		val pizzaToppings: Seq[String],
		val dietRestrictions: Seq[String]
	)

Without the extension to juice we'd end up just using a regular `@Provides`
annotation and praying nothing goes wrong. This might look something like 
this within a module:

	import com.google.inject.{AbstractModule, Provides}
	import com.typesafe.config.ConfigFactory

	class PizzaModule extends AbstractModule {

		def configure {}

		@Provides
		def provideDataSourceParams() = {
			val conf = ConfigFactory.load() // Might throw an exception!
			val url = new URL(conf.getString("dsp.url")) // Might throw an exception!
			val accessCode = conf.getString("accessCode") // Might throw an expcetion!
			DataSourceParams(url, accessCode)
		}

		@Provides
		def provideRemotePizzaOrder(dataSourceParams: DataSourceParams) = {
			val conf = ConfigFactory.parseURL(dataSourceParams.url) // Might throw an exception
			RemotePizzaOrder(
				conf.getLong("rpo.numberOfPizzas"),
				conf.getStringList("rpo.pizzaToppings"),
				conf.getStringList("rpo.dietRestrictions")
			) // Any of the conf.get* might throw an exception
		}
	}
	

If anything goes wrong with this, from the URL being malformed, to a 
configuration property not being set, we're going to get a runtime 
exception from Guice. For example, if without setting up a configuration 
file I were to run this code:

	val injector = Guice.createInjector(new PizzaModule)
	val databaseParams = injector.getInstance(classOf[DataSourceParams])

I'd get a stacktrace like this:

	com.google.inject.ProvisionException: Unable to provision, see the following errors:

	1) Error in custom provider, com.typesafe.config.ConfigException$Missing: No configuration setting found for key 'dsp'
	  at Example$PizzaModule.provideDataSourceParams(TEST.scala:25)
	  while locating Example$DataSourceParams

	1 error
	  at com.google.inject.internal.InjectorImpl$2.get(InjectorImpl.java:1028)
	  at com.google.inject.internal.InjectorImpl.getInstance(InjectorImpl.java:1054)
	  at Example$.delayedEndpoint$Example$1(TEST.scala:43)
	  at Example$delayedInit$body.apply(TEST.scala:9)
	  at scala.Function0$class.apply$mcV$sp(Function0.scala:34)
	  at scala.runtime.AbstractFunction0.apply$mcV$sp(AbstractFunction0.scala:12)
	  at scala.App$$anonfun$main$1.apply(App.scala:76)
	  at scala.App$$anonfun$main$1.apply(App.scala:76)
	  at scala.collection.immutable.List.foreach(List.scala:381)
	  at scala.collection.generic.TraversableForwarder$class.foreach(TraversableForwarder.scala:35)
	  at scala.App$class.main(App.scala:76)
	  at Example$.main(TEST.scala:9)
	  ... 42 elided
	Caused by: com.typesafe.config.ConfigException$Missing: No configuration setting found for key 'dsp'
	  at com.typesafe.config.impl.SimpleConfig.findKey(SimpleConfig.java:124)
	  at com.typesafe.config.impl.SimpleConfig.find(SimpleConfig.java:147)
	  at com.typesafe.config.impl.SimpleConfig.find(SimpleConfig.java:159)
	  at com.typesafe.config.impl.SimpleConfig.find(SimpleConfig.java:164)
	  at com.typesafe.config.impl.SimpleConfig.getString(SimpleConfig.java:206)
	  at Example$PizzaModule.provideDataSourceParams(TEST.scala:26)
	  at Example$PizzaModule$$FastClassByGuice$$6f73dc9a.invoke(<generated>)
	  at com.google.inject.internal.ProviderMethod$FastClassProviderMethod.doProvision(ProviderMethod.java:264)
	  at com.google.inject.internal.ProviderMethod$Factory.provision(ProviderMethod.java:401)
	  at com.google.inject.internal.ProviderMethod$Factory.get(ProviderMethod.java:376)
	  at com.google.inject.internal.InjectorImpl$2$1.call(InjectorImpl.java:1019)
	  at com.google.inject.internal.InjectorImpl.callInContext(InjectorImpl.java:1085)
	  at com.google.inject.internal.InjectorImpl$2.get(InjectorImpl.java:1015)
	  ... 53 more
	
Which is not something we'd want to be presenting to a user. Because 
we're using the `@Provides` method the exception is thrown _within_ 
Guice, which is why we get a ProvisionException and are unable to handle 
the `ConfigException.Missing` exception. We'd rather catch such 
exceptions and handle them more gracefully. 

According to the Guice wiki, the limitations of regular providers are:

- Implementers of Provider can only throw RuntimeExceptions.
- Callers of Provider can't catch the exception they threw, because it may be wrapped in a ProvisionException.
- Injecting an instance directly rather than a Provider can cause creation of the injected object to fail.
- Exceptions cannot be advertised in the API.

This is where the CheckedProvider's come in. 

### Pushing exception handling to application scope with CheckedProvider

A `CheckedProvider` allows you to push the error handling for _a provider 
of that type_ out to whatever is supposed to be getting an instance in 
your code. This means that there is a level of indirection from guice 
crossing into application space where we must handle the specific 
exceptions we know will be thrown. This is obvious if you note in the 
documentation for [CheckedProvider] that it says:

>Users may not inject T directly.

However if you rush over to use the annotation thinking that it works like
`@Provides` and that you'll get a type `T` on injection from a 
`CheckedProvider[T]` you might miss this note (like I did the first time 
I looked at this). So don't do that. You need to be aware that when 
you're injecting you need to take the _providing interface_ of the type, 
and not the type itself wherever you're planning on injecting.

So firstly, we define the interface which will be used by Guice. This is 
just an interface defining what we can get and what exceptions it throws. 
In Java you'd use the `throws` keyword, but in scala there's no such 
thing, so you just annotate it for any Java code that might call your 
own code to have the same effect.
	
	import java.net.MalformedURLException

	trait DataSourceProviderLike extends CheckedProvider[DataSourceParams] {
		@throws(classOf[ConfigException])
		@throws(classOf[MalformedURLException])
		def get(): DataSourceParams
	}

	trait RemotePizzaOrderProviderLike extends CheckedProvider[RemotePizzaOrder] {
		@throws(classOf[ConfigException])
		def get(): RemotePizzaOrder
	}

Once you have the trait defined, you need to install it or bind it in 
your module. If you're using the `@CheckedProvides` annotation you'll 
want to use `install`:
	
	class SaferPizzaModuleInstalled extends AbstractModule {
		def configure() {
			install(ThrowingProviderBinder.forModule(this))
		}

		@CheckedProvides(classOf[DataSourceProviderLike])
		def provideDataSourceParams() = {
			val conf = ConfigFactory.load() // Might throw an exception!
			val url = new URL(conf.getString("dsp.url")) // Might throw an exception!
			val accessCode = conf.getString("dsp.accessCode") // Might throw an expcetion!
			DataSourceParams(url, accessCode)
		}
		...
	}

And if you're binding the interface to a concrete class you'll put your 
loading logic into that implementation and use `ThrowingProviderBinder`'s 
static methods:

	class DataSourceProvider extends DataSourceProviderLike {
		@throws(classOf[ConfigException])
		@throws(classOf[MalformedURLException])
		def get() = {
			val conf = ConfigFactory.load()
			val url = new URL(conf.getString("dsp.url"))
			val accessCode = conf.getString("dsp.accessCode")
			DataSourceParams(url, accessCode)
		}
	}

	def configure() {
		...
		ThrowingProviderBinder.create(binder())
			.bind(classOf[DataSourceProviderLike], classOf[DataSourceParams])
			.to(classOf[DataSourceProvider]) 
		...
	}

Annotations or directly using the binding calls is up to you as it's 
more of a matter of personal preference here. Here's a full example to 
look at:

<script src="https://gist.github.com/EdgeCaseBerg/c25ec3d57a8622d08cafed2a1b7d320b.js"></script>

#### Ok... So?

It was at this point in my adventure through Guice's documentation and 
wiki that I asked myself: "What's the difference between this and just 
using a plain interface?". After all, If in order to use the 
`CheckedProvider` I have to update my constructors or other code to take 
the interface anyway, how does using a `CheckedProvider` give me anything
more? After all, I can provide an interface that's been bound to a 
concrete class and scope it with a regular provider. The _only_ shift in 
using a `CheckedProvider` is that it forces calling code to handle the 
`.get` call and its possible exceptions rather than allow the creation 
of an instance to fail within the framework. And that's more of a 
mentality shift than anything else because if you were to update to use 
interfaces anyway, you'd have to do that regardless. 

The only thing right now that I can think of that this helps is if 
you're coding in Java and not Scala, because Scala doesn't complain like 
Java's compiler about `throws`, I've never had to deal with `Provider` 
not being able to throw anything but runtime exceptions and not the 
specific exception to be caught. So I might be missing context here.

I hope that this helps provide a clearer example of how to use the 
`CheckedProvider` and `ThrowingProviderBinder` than the guice wiki's 
because I had a bit of a time deciphering what all of that meant without 
a full example illustrating the full technique. And I'm thinking that 
because of this, I might still not be fully understanding how using the 
`CheckedProvider`s improves ones code in a way that you couldn't do 
without it.


	



[guice wiki]:https://github.com/google/guice/wiki/ProvidesMethods#throwing-exceptions
[getting started]:https://github.com/google/guice/wiki/GettingStarted
[motivation]:https://github.com/google/guice/wiki/Motivation
[typesafe's config library]:https://github.com/typesafehub/config
[ConfigException subclasses]:https://typesafehub.github.io/config/latest/api/com/typesafe/config/ConfigException.html
[JavaDoc]:https://google.github.io/guice/api-docs/latest/javadoc/com/google/inject/throwingproviders/CheckedProvider.html
[extension's JavaDoc]:https://google.github.io/guice/api-docs/latest/javadoc/com/google/inject/throwingproviders/package-summary.html
[I found what I needed]:https://search.maven.org/#search%7Cga%7C1%7Cg%3A%22com.google.inject.extensions%22
[CheckedProvider]:https://google.github.io/guice/api-docs/latest/javadoc/com/google/inject/throwingproviders/CheckedProvider.html