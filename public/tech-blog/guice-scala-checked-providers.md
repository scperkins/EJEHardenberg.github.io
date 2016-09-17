### Guice Scala & CheckedProviders

**Note:**
_If you're unfamiliar with guice, I highly recommend reading the 
[getting started] or the [motivation] before continuing so you have the 
basic concepts of the library down._

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







[guice wiki]:https://github.com/google/guice/wiki/ProvidesMethods#throwing-exceptions
[getting started]:https://github.com/google/guice/wiki/GettingStarted
[motivation]:https://github.com/google/guice/wiki/Motivation
[typesafe's config library]:https://github.com/typesafehub/config
[ConfigException subclasses]:https://typesafehub.github.io/config/latest/api/com/typesafe/config/ConfigException.html