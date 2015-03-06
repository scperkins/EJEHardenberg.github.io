### Write your own init script

Most developers who've written web software know that when they install 
something like [httpd] they can typically call `service httpd restart` 
and they'll restart their server. Similarly, they could call 
`/etc/init.d/httpd start` to start, or change start to `stop` and they'll
shut off the server. All of this is typically web-dev 101. 

But what happens when you write your own server? And how does that service 
call work?

On a linux machine there's a concept of _runlevels_. These indicate the 
state of your machine. And when you transition into one of these states 
there are scripts that can be ran automatically. To manage these you can 
use `chkconfig`. If you call `chkconfig --list` you'll see a list of 
various services and which run levels they're active on. I won't attempt 
to go fully in depth on run levels, but you should read [about them here] 
and then come back to this post once you're finished. 

Back? Alright, now that we know all about run levels, and we've discovered 
that we only need to write one script that will be symlinked like crazy 
from all those _rcN.d_ directories. So what goes into this script?

Well, the template is pretty simple to follow. It goes like this:

	#!/bin/sh
	#
	# /etc/init.d/myservice
	# init script for "MyService" server
	#
	# chkconfig: 036 95 05
	# description: MyServer server daemon
	#
	# processname: MyServer
	# pidfile: /var/run/MyServer.pid
	
	RETVAL=0
	prog="MyServer"
	
	start() {
		echo -n $"Starting $prog:"
		nohup MyServer &
		echo $! > /var/run/MyServer.pid
		echo
	}
	
	stop() {	(6)
		echo -n $"Stopping $prog:"
		if [ -f /var/www/run/MyServer.pid ]; then 
			kill `cat /var/www/run/MyServer.pid`
			rm /var/www/run/MyServer.pid
		fi
		echo
	}
	
	case "$1" in
		start)
			start
			;;
		stop)
			stop
			;;
		restart)
			stop
			start
			;;
		*)	(10)
			echo $"Usage: $0 {start|stop|restart}"
			RETVAL=1
	esac
	exit $RETVAL

The first part of this script consists of a large block of comments. These 
are known as _tags_ for the init system to read. The `chkconfig:` and 
`description:` tags are the only required ones and have an important role 
to play. The description tag tells you what this script is all about 
(documentation is important you know?). The chkconfig is special, those 
three numbers set the run levels this script is called from, the priority 
in which the script is ran when started, and the priority when the script 
is called with stop. These last two numbers should add up to 100.

For a description of each of the tags you can use, you can [read more here]. 
I've chosen run levels 0,3 and 6 so that the service is called whenever the 
machine is stopped or rebooted, and when we've acquired networking capabilities.

The one fancy trick here is the following:

	nohup MyServer &
	echo $! > /var/run/MyServer.pid

The `$!` (dollarsign bang), within a bash shell, recieves the process id of the 
program which was pushed to the background last. Don't ask me how to google for 
that symbol (it's hard), but that's what it does, and when combined with the 
[nohup] command, it makes for an easy way to grab the process ID of your new 
service.

Make sure your script doesn't have any syntax errors and move it to the /etc/init.d/
directory. Make sure it's executable via `chmod +x scriptname` and give it a couple 
of goes. Depending on what your service is capable of responding to, you may add 
in other options like `status`, `reload`, etc. If you want to see all the options 
for what you can use in the case statement, you can read more [here]. 

Once the script is in place simply run `chkconfig` using the name of the script 
in the init.d directory like so:

	chkconfig --add myservice
	chkconfig --list myservice
	myservice   0:on   1:off   2:off   3:on    4:off   5:off    6:on

And that's it! If you change the runlevels in the tags of the script you'll want 
to do a quick `chkconfig --del myservice && chkconfig --add myservice` to update
the run levels. Now go forth! Write your own services!

[httpd]:https://httpd.apache.org/
[about them here]:http://www.linuxjournal.com/article/1274
[read more here]:http://www.sensi.org/~alec/unix/redhat/sysvinit.html
[nohup]:http://linux.die.net/man/1/nohup
[here]:http://www.sensi.org/~alec/unix/redhat/sysvinit.html