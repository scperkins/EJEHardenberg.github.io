### Set netty timeout options in Play

As you may or may not know, the [Playframework] runs on top of [Netty].
This means that when you're configuring the server aspects of your 
application, at some point you're going to want to set the options on 
Netty itself. The [documentation for production configuration] is fairly 
useful in this, providing a few examples of the properties you can set, 
and even detailing how to pass any option to the server underneath. 

The one thing it doesn't do is tell you how to _get_ the options to the 
server in the first place. Unless you're in the business of passing along 
options to your applications you might not realize that _every_ new option 
to netty needs to be passed on startup via a `-D` parameter. Keeping track 
of this is a pain, after all, what about when you have multiple environments 
and you need to tweak each one? 

While looking around, I found a [smart guy] who might not have read the 
documentation page I linked above. And this blog post goes out to him on 
a simpler way to set Netty options. First off you need to recognize two 
things. 

1. Using the `dist` command will create a startup script
2. Hidden in this startup script is a way to add configuration easily

If you look into the file named after your application in the dist's bin 
directory you'll find the following piece of bash script:
	
	declare -r script_conf_file="/etc/default/yourappnamehere"
	...
	# if configuration files exist, prepend their contents to $@ so it can be processed by this runner
	[[ -f "$script_conf_file" ]] && set -- $(loadConfigFile "$script_conf_file") "$@"

The `loadConfigFile` is fairly simple:

	# Loads a configuration file full of default command line options for this script.
	loadConfigFile() {
	  cat "$1" | sed '/^\#/d'
	}

In essence, whatever you put into the config file will be appended to your
startup. So if you were to say, add `-Dhttp.netty.option.child.connectTimeoutMillis=600000` 
you'd endup setting the timeout to 10 minutes for your netty server running 
your play application. Useful right? If you're [Yevgeniy Brikman] this one line: 

	-Dhttp.netty.option.backlog

in an `/etc/default/myapp` file would have saved you a lot of trouble. 
Since play doesn't write the Netty configuration to a logfile for you 
on startup, verifying that the settings are in place required me to 
check the JVM itself. This was easily done by using [VisualVM] to connect 
to my [Docker container]. If you want instructions on how to do that, 
you can check my [previous post here]. Then check the `ServerBootstrap`
class instance on the heap and look in the options HashMap:

<img style="max-width:100%" src="/images/tech-blog/visualvm.png">



[Playframework]:https://playframework.com
[Netty]:http://netty.io/
[documentation for production configuration]:https://www.playframework.com/documentation/2.2.x/ProductionConfiguration
[smart guy]:http://www.ybrikman.com/writing/2014/02/18/maxing-out-at-50-concurrent-connections/
[Yevgeniy Brikman]:http://www.ybrikman.com/
[VisualVM]:https://visualvm.java.net/
[Docker container]:https://www.docker.com/what-docker
[previous post here]:connect-visualvm-docker
