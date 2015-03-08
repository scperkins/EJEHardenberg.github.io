### Green Up 2015 

Last year I [wrote about Green Up] and my use of [varnish] to cache the 
[API server] that was created to service the various applications [Xenon Apps] 
created for the [Green Up Vermont NPO]. 

This year we're running the same setup for them, and this past weekend I 
got together with the other developers and reworked the server for the 
API. It's running a pretty small stack:

- [Varnish]
- [C API]
- [ufw]

And that's it. The machine is _small_, running with only 256MB of RAM. 
It might surprise you that this is the same machine that serviced the 
300 or so users of the application last year. 

#### Varnish

Varnish is performing the same duties as last year, acting as [backend 
director] and load balancer for the running instances of the C APIs. 
The full configuration file uses 2 backends right now and also enables 
the CORS headers for varnish during the delivery phase. Here's the full 
vcl file:

	backend default {
	    .host = "127.0.0.1";
	    .port = "31337";
	    .probe = {
		.url ="/api/";
		.interval = 10s;
		.timeout = 2s;
		.window = 5;
		.threshold = 3;
	    }
	}
	
	backend backup {
	    .host = "127.0.0.1";
	    .port = "31338";
	    .probe = {
		.url ="/api/";
		.interval = 10s;
		.timeout = 2s;
		.window = 5;
		.threshold = 3;
	    }
	}
	
	sub vcl_recv {
		if ( req.request == "POST" || req.request == "PUT" ) {
			#Invalidate only the neccesary things per endpoint
			if ( req.url ~ "(?i)/api/comments" ) {
				ban("req.url ~ (?i)/api/comments");
				ban("req.url ~ (?i)/api/pins");
			}
			if ( req.url ~ "(?i)/api/pins" ) {
				ban("req.url ~ (?i)/api/comments");
				ban("req.url ~ (?i)/api/pins");
			}
			if ( req.url ~ "(?i)/api/heatmap" ) {
				ban("req.url ~ (?i)/api/heatmap");
			}
			if( req.url ~ "(?i)/api/debug" ) {
				ban("req.url ~ (?i)/api/debug");
			}
			#Don't cache POST or PUT (no sense in doing so)
			return(pass);
		}
	}
	
	director backup_director round-robin {
		{
			.backend = default;
		}
		{
			.backend = backup;
		}
	}
	
	sub vcl_fetch { 
		set req.backend = backup_director;
	}
	
	sub vcl_deliver {
		set resp.http.Access-Control-Allow-Origin = "*";
		set resp.http.Access-Control-Allow-Methods = "GET, POST, PUT, DELETE";
		set resp.http.Access-Control-Allow-Headers = "Content-Type";
		
		if (obj.hits >= 0)
		{
			set resp.http.X-Cache = "HIT";
		}
		else
		{
			set resp.http.X-Cache = "MISS";
		}
	}

You'll notice the invalidation on the POST requests is exactly the same 
as it was [last year]. And also the header X-Cache is handy for debugging 
if you're recieving a cached result or not.

#### API Servers 

Something that is a little bit different this year is the way which the 
API servers are setup. Last year my system admin hat wasn't quite so 
feathered, this year, I've got a new set of tools to apply. Specifically, 
[subsystem scripts].

I started out by deciding how best to organize the multiple copies of  
the API servers that would run, deciding on a simple directory structure 
inside _/var/run/_ directory. I created a green-serv folder, and then 
for each instance of the API running I created a folder based on the 
port it would listen in on. So in the end I had 3 folders setup:

	user@server:/var/run/green-serv# ls
	31337  31338  80  

This was done to make it easier to start up multiple instances of the 
server itself. If we take a look at the script I wrote for the service:

	#!/bin/sh
	#
	# Subsystem file for green-serv
	#
	# chkconfig: 036 95 05
	# description: green-serv
	#
	
	# To install: 
	#   chmod +x, mv to /etc/init.d/green-serv, then chkconfig --add green-serv
	
	RETVAL=0
	prog="green-serv"
	PORT="80"
	if [ $# -eq 2 ]; then
		PORT=$2
	fi
	PID_FILE=/var/run/green-serv/$PORT/GREENSERV_PID.pid
	PORT_FILE=/var/run/green-serv/$PORT/GREENSERV.port
	CMD=/var/run/green-serv/$PORT/green-serv
	LOGFILE=/var/log/green-serv.log
	
	start() {
		echo -n $"Staring $prog:"
		echo $PORT > $PORT_FILE
		nohup $CMD >> $LOGFILE 2>&1 &
		echo
	}
	
	stop() {
		echo -n $"Stopping $prog:"
		if [ -f $PID_FILE ]; then kill `cat $PID_FILE`; fi
		echo
	}
	
	if [ "$(id -u)" != "0" ]; then
		echo "This script must be run as root" 1>&2
		exit 1
	fi
	
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
		*)
			echo $"Usage: $0 {start [port]|stop [port]|restart}"
			RETVAL=1
	esac
	exit $RETVAL

You might notice that unlike your common service file such as apache or 
mysql, this one can take an additional argument! Specifically, doing 
something like this: `service green-serv start 3000` would start up a 
server instance on port 3000 (as long as that directory exists and has 
the server binary). 

A couple changes I made today on the API server was to have it write its 
own [process id to a file], and to [load which port to run on from a file 
within the same directory as the binary]. This helped facilate this script 
to be an easy one to write. 

In addition, I updated the [Makefile] to have an `install` command to 
make deploying any changes out to the various run folders easy:

	install:
		mkdir -p /var/run/green-serv/80
		for portdir in `ls -d /var/run/green-serv/*/`; do \
			cp green-serv $$portdir;\
		done
		chmod +x green-serv.d
		cp green-serv.d /etc/init.d/green-serv

This is pretty standard, and only handles just an 80 port as far as 
creating goes, but it does support updating the binaries for any directory 
in the green-serv run folder. The only thing to make note of is the weird 
`$$portdir` -- which if you're familiar with bash will make you assume that 
I had a typo and wrote 2 dollar signs instead of one. Nope, within a Makefile 
you need two dollar signs in order to differentiate the make and bash variables 
from one another.

#### UFW

The last thing to setup was a firewall. The uncomplicated firewall (ufw) 
is, as its name implies, uncomplicated. A few simple commands are all you 
really need:

	cat /etc/ufw/applications.d/varnish
	[Varnish]
	title=Web Proxy
	description=Proxy caching server
	ports=80/tcp

	sudo ufw allow OpenSSH
	sudo ufw allow Varnish
	sudo ufw default deny
	sudo ufw enable

And you're pretty much all set. Ports that aren't used by the applications 
listed in _/etc/ufw/applications.d_ will be denied by default. Note that 
you probably want to triple check that you've allowed SSH through so you 
don't kill your connection to your server. A good rule of thumb is to 
enable the ports you're using for SSH, then enable the firewall and try 
to ssh to the server _from a different shell_ and if it doesn't work, 
disable the firewall and try again with different settings.

The firewall is in place to make sure that the API servers are only 
accessed through Varnish and not from the outside world. This enables us 
to be sure that varnish will handle all the load and we won't tax our 
servers from the outside world by anything.

#### Summary

In conclusion, the API server is ready to go for round two of Green Up 
day and we're all hoping that it will go as smoothly as it did last year!

[wrote about Green Up]:/tech-blog/green-up-vt-app
[varnish]:/tech-blog/varnish
[Varnish]:https://www.varnish-cache.org
[API server]:https://github.com/EdgeCaseBerg/green-serv
[Green Up Vermont NPO]:http://greenupvermont.org
[C API]:https://github.com/EdgeCaseBerg/green-serv
[ufw]:https://help.ubuntu.com/community/UFW
[Xenon Apps]:http://www.greenupvermont.org/?page_id=788
[backend director]:https://www.varnish-cache.org/docs/3.0/tutorial/advanced_backend_servers.html#directors
[last year]:http://www.ethanjoachimeldridge.info/tech-blog/varnish
[subsystem scripts]:http://www.ethanjoachimeldridge.info/tech-blog/write-your-own-init-scripts
[process id to a file]:https://github.com/EdgeCaseBerg/green-serv/commit/1ff34c78e11eb954af15802ab33a8a9bfec39ac3
[load which port to run on from a file within the same directory as the binary]:https://github.com/EdgeCaseBerg/green-serv/commit/7c216c95944358f6a5164f896af245830c7b4074
[Makefile]:https://github.com/EdgeCaseBerg/green-serv/blob/master/Makefile