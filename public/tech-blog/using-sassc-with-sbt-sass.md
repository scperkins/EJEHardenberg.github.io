### Using sassc with sbt-sass

Today I was watching my coworker wait for about 15 minutes or so while 
installing node, npm, and grunt, all for the purpose of compiling sass 
assets. While waiting, I did a little bit of searching and ended up 
finding the [play-sass] plugin for play. 

My fellow developer, being opinionated about the version of sass he 
uses had passed over the plugin after seeing `gem install sass`. 
Preferring a C++ version he had installed which was ran by his 
javascript setup (I'd call it bloat). However, on closer reading, I 
noticed that the readme file stated

>Sass compiler needs to be installed for plugin to work. This means that sass executable needs to be found in path. 

While it was suggested by the plugin to use ruby's sass gem, we only 
_actually_ need the executable in the environment. Armed with this 
information. I stepped out to prove that we could get by without 
introducing an army of package, gulp, and install.js files into our 
code base.

It wasn't difficult. Compiling [libsass] is pretty easy if you can 
follow instructions, and then choosing an [implementation] was easy. 
For my purposes, and being a [lover of c], I chose to use [sassc]. 
Installing sassc was simple, one can build it from source or use any 
mature package manager to do so. For example, on a Mac you might run:

	brew install sassc

And be done with it. On linux, a similar call to `apt-get` and you'd be 
all set. The one kicker is that the binary for sassc is named, 
unsurprisingly, `sassc` and not `sass` like the plugin requires. This 
is trivially solved with a sym link though:

	ln -s /usr/local/bin/sassc /usr/local/bin/sass

Once this is done, you're all set to run sbt! Within your play templates 
you can call out to your assets like so:

	<link rel="stylesheet" href="@routes.Assets.at("sass/main.css")">

And this will use the compiled version of the file "sass/main.scss"!
The additional plus is that since this is hooked directly into play 
whenever you save an asset file, the files will be updated appropriately. 

Now I don't have a dependency on node, npm, or anything like that, and 
can compile sass with blindingly fast c. The only cost is that others 
will need to install sass in order to run the application. But when I 
consider that it took maybe 5 minutes at most to install sassc, and 2 
seconds to setup a sym link. It's a fair cost.

[play-sass]:https://github.com/jlitola/play-sass
[libsass]:https://github.com/sass/libsass
[implementation]:https://github.com/sass/libsass/wiki/Implementations
[lover of c]:/tech-blog/cgi-c-harp-1
[sassc]:https://github.com/sass/sassc