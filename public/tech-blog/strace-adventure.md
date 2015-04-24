### An Adventure in `strace` 

Troubleshooting bugs is not always as simple as reading an error log. 
Today I ended up running end to end in order to track down a 
relatively simple bug, which, like all bugs, was obvious and trivial 
to fix once the logic behind the issue was understood.

I started off my day thinking I'd deploy some code to a staging 
environment. Nothing too exciting about that, after all, yesterday I 
had deployed some code and went home and left a long running process 
on over night. In the morning I checked that my import had finished 
and got to work. 

After updating the source code and deploying to the environment I ran 
into a wall. Specifically a [504 Error]. Confused about the timeout, I 
`ssh`-ed to the server and checked the log files. This particular server 
had an [nginx] server that proxied back to an [apache] instance. Looking 
through the logfiles I saw a single error message:

	client closed connection while waiting for request, client: xx.xxx.xxx.xx:8080, server: 0.0.0.0:80

Mildly confused, I tested the apache server in the background via `curl` 
and found it returning the expected 401. Authenticating with the `--user` 
flag and everything hung. No timeout (even after 5 minutes), nothing in 
the log files for apache. Nothing. 

Confused, I started troubleshooting my nginx configuration, fiddling with 
parts of it to make sure that each server was proxying back to the 
configured instance or application. Every single virtual host on apache 
and server configuration in nginx worked _except for the one I was testing_. 

After using `httpd -S` to make sure that my default virtual host wasn't 
incorrect I quickly wrote a test script.

    <?php echo "Yeah, I'm working..."; ?>

And on testing it I saw that the server itself was working: 

	curl --user user:password localhost:8080/test.php
	#Yeah, I'm working...

So then the error must be in the application. I bumping up the logging in 
`curl` via the `--verbose` flag to see if there was an infinite redirect 
going on, but that returned unfruitful. "So the error must be in the 
application" I thought. Checking the error logs showed nothing, so I
figured there might be an infinite loop or something of that nature. So
I dug out the trusty tool [strace].

`strace` allows you to view the system calls of a running application 
by attaching to it. In order to use it one typically uses `ps` to or 
`pidof` to determine the process id, then specifies this id in the `-p` 
flag. When it comes to debugging a daemonized application such as httpd 
or mysql you'll also need to use the `-f` flag to _follow_ any forked 
processes. 

So if the output of `ps aux | grep apache` looks like this:

	root      2742  0.0  0.1 420428  9508 ?        Ss   Apr21   0:12 /usr/sbin/apache2 -k start
	www-data 16117  0.0  0.0 420516  7288 ?        S    Apr22   0:00 /usr/sbin/apache2 -k start
	www-data 16118  0.0  0.0 420516  7288 ?        S    Apr22   0:00 /usr/sbin/apache2 -k start
	www-data 16119  0.0  0.0 420484  7052 ?        S    Apr22   0:00 /usr/sbin/apache2 -k start
	www-data 16120  0.0  0.0 420484  7052 ?        S    Apr22   0:00 /usr/sbin/apache2 -k start
	www-data 16121  0.0  0.0 420484  7052 ?        S    Apr22   0:00 /usr/sbin/apache2 -k start

Then you would want to use `strace -f -p 2742` to monitor any additional 
processes created. Or, to be sure, you could make use of the fact that 
the `-p` flag can be used multiple times and monitor the already forked 
processes like so: 

	strace -f -p 2742 -p 16117 -p 16118 -p 16119 -p 16120 -p 16121

And you'll see an output something like this:


	Process 2742 attached - interrupt to quit
	Process 16117 attached - interrupt to quit
	Process 16118 attached - interrupt to quit
	Process 16119 attached - interrupt to quit
	Process 16120 attached - interrupt to quit
	Process 16121 attached - interrupt to quit
	[pid  2742] select(0, NULL, NULL, NULL, {0, 574545} <unfinished ...>
	[pid 16120] semop(131072, {{0, -1, SEM_UNDO}}, 1 <unfinished ...>
	[pid 16121] semop(131072, {{0, -1, SEM_UNDO}}, 1 <unfinished ...>
	[pid 16119] semop(131072, {{0, -1, SEM_UNDO}}, 1 <unfinished ...>
	[pid 16118] semop(131072, {{0, -1, SEM_UNDO}}, 1 <unfinished ...>
	[pid 16117] epoll_wait(47,  <unfinished ...>
	[pid  2742] <... select resumed> )      = 0 (Timeout)
	[pid  2742] wait4(-1, 0x7fff8200f2ac, WNOHANG|WSTOPPED, NULL) = 0
	[pid  2742] select(0, NULL, NULL, NULL, {1, 0}) = 0 (Timeout)
	[pid  2742] wait4(-1, 0x7fff8200f2ac, WNOHANG|WSTOPPED, NULL) = 0
	[pid  2742] select(0, NULL, NULL, NULL, {1, 0}^C <unfinished ...>
	Process 2742 detached
	Process 16117 detached
	Process 16118 detached
	Process 16119 detached
	Process 16120 detached
	Process 16121 detached

Of course this doesn't get more interesting than your regular event 
polling loop until the server responds to something or is asked to 
execute code by the application. In my case, the first breadcrumb 
appeared as an error in resolving an ip address:


    [pid   904] connect(32, {sa_family=AF_INET, sin_port=htons(3306), sin_addr=inet_addr("192.168.100.194")}, 16) = -1 EINPROGRESS (Operation now in progress)
    [pid   904] fcntl(32, F_SETFL, O_RDWR)  = 0
    [pid   904] poll([{fd=32, events=POLLIN|POLLPRI}], 1, 60000 <unfinished ...>
    ...
    [pid   904] setsockopt(32, SOL_SOCKET, SO_SNDTIMEO, "\2003\341\1\0\0\0\0\0\0\0\0\0\0\0\0", 16 <unfinished ...>
    ...
    [pid   904] <... read resumed> 0x7f2bfe23c8d0, 16384) = -1 ETIMEDOUT (Connection timed out)

Anyone who's ever dealt with the [c networking apis] knows that the 
`inet_addr` function is used to convert a human readable ip to a machine 
readable form, and then this is used by the `connect` call to actually 
perform the connection. We're lucky in this case, as we can very easily 
see the IP address that is being attempted to resolve. 

Any ip address that looks like `192.164.x.x` is a [private IP], which 
means that it's internal to the subnetwork of the machines. In this 
case, the ip address couldn't be resolved. Why? Simple. The ip address 
belonged to the production environment and not the staging one. 

Of course, I only realized this after I had run off to look at another 
system first. If you note that call to `htons` is using the port 3306 it 
should be clear which application. If you're not used to web development 
involving [mysql], then that's ok, but 3306 is the standard mysql port. 

While `strace`ing the mysql process I saw a flurry of activity when I 
ran up the application (A [Drupal 6] Installation) and after the browser 
continued spinning, I saw an insert statement fly by. Noting that it was a 
logging query from the [watchdog] function. I checked out the table in 
the database: 

	SELECT * FROM watchdog ORDER BY timestamp DESC LIMIT 20\G
	
	| 188148200 |   0 | php  | %message in %file on line %line. | a:4:{s:6:"%error";s:7:"warning";s:8:"%message";s:67:"mysql_close(): supplied argument is not a valid MySQL-Link resource";s:5:"%file";s:67:"/var/www/sites/all/modules/cdn/cdn.advanced.inc";s:5:"%line";i:82;}                                                                                                          |        3 |      | http://staging.example.com/ |         | 127.0.0.1 | 1429902803 |
	+-----------+-----+------+---------------------------
	...

Aha! As `strace` had indicated, we were failing on connecting to a mysql 
database somewhere in the code. And according to the watchdog error, it 
was coming from the [cdn module]. After grepping the code base I found 
the variables used to specify the configuration of the module and noted 
that the same mysterious IP address appeared there as well. 

At that point the gears clicked and the realization that the file 
conveyer processes that migrated any uploaded images from the site 
admins to the CDN occured. This is a process which doesn't happen on the 
staging environment I was troubleshooting, and had slipped in from a 
database import that I had left running over night.

So the answer was pretty simple to fix the issue. **Disable the CDN Module**. 
However, due to... circumstances, [drush] wasn't available to me in the  
environment I was in. This meant I had to toggle the module the old 
fashioned way, via SQL.

	update system set status = 1 where name = 'cdn';

This was enough to get _most_ of the application up and running and I 
was able to see a header appear, however an error appeared in my logs 
until I reset some of the values for the cdn in the cache:

	update cache set data = replace(data, '"cdn_status";s:1:"0";','"cdn_status";s:1:"1";') where data like '%cdn_status%';
	update variable set value = 's:1:"0";' where name like 'cdn_status';

After that the application loaded and I was able to verify, after a 
few hours of banging my head against server configurations, system 
logs, and network scanning, that the minute changes I had deployed 
were working. 

#### The take away?

When your regular application logs fail, tools like `strace` or [sysdig] 
can really come in handy.


[504 Error]:http://en.wikipedia.org/wiki/List_of_HTTP_status_codes#5xx_Server_Error
[nginx]:http://nginx.org/
[apache]:http://www.apache.org
[strace]:http://sourceforge.net/projects/strace/
[c networking apis]:http://beej.us/guide/bgnet/output/html/singlepage/bgnet.html#datagram
[private IP]:http://compnetworking.about.com/od/workingwithipaddresses/f/privateipaddr.htm
[mysql]:https://dev.mysql.com/
[Drupal 6]:https://www.drupal.org/project/drupal
[watchdog]:https://api.drupal.org/api/drupal/includes%21bootstrap.inc/function/watchdog/6
[cdn module]:https://www.drupal.org/project/cdn
[drush]:https://www.drupal.org/project/drush
[sysdig]:http://www.sysdig.org/
