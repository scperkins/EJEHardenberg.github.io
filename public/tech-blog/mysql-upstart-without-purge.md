### Fixing mysql Upstart problems without purging your system

A few months ago I installed the newest version of mysql, at the same 
time, I foobarred half my system and then had to uninstall my old version 
to get anything done. At the end of a long debugging session I had two 
versions of mysql working under different services. All was good.

Or at least that's what I thought. Today I was looking through my logs 
wondering why the crash report log (apport) was so huge. When nothing particularly 
interesting appeared in those logs, I decided to take a peak into the dbus 
log.


    $ dbus-monitor --system
	signal sender=:1.0 -> dest=(null destination) serial=4655 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=GoalChanged
	   string "respawn"
	signal sender=:1.0 -> dest=(null destination) serial=4656 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=GoalChanged
	   string "start"
	signal sender=:1.0 -> dest=(null destination) serial=4657 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "stopping"
	signal sender=:1.0 -> dest=(null destination) serial=4658 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "killed"
	signal sender=:1.0 -> dest=(null destination) serial=4659 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "post-stop"
	signal sender=:1.0 -> dest=(null destination) serial=4660 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "starting"
	signal sender=:1.0 -> dest=(null destination) serial=4661 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "pre-start"
	signal sender=:1.0 -> dest=(null destination) serial=4662 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "spawned"
	signal sender=:1.0 -> dest=(null destination) serial=4663 path=/com/ubuntu/Upstart/jobs/mysql/_; interface=com.ubuntu.Upstart0_6.Instance; member=StateChanged
	   string "post-start"

Well, that doesn't look good. And When I looked around on the internet for a 
solution I ran into [this post] which said to just purge everything and start 
over. To me, that seems a bit silly, especially when I have so much data stored 
on my system and don't feel like waiting to re-import everything.

So I asked myself how bad was it?

	$sudo sysdig -c fdcount_by proc.name "fd.type=file"
	mysqld	814
	BrowserBlocking	413
	irqbalance	30

I ran the above chisel for about 10 seconds or so, so pretty bad. Tailing 
the mysql error log gives me a continous stream of mysql's service trying 
to start and stop over and over again, seemingly hung up on InnoDb issues.

Of course, my browser rules the I/O errors here, a quick run of `sysdig -c topprocs_errors` 
shows me that I've got 200+ errors on each refresh (once per second or so). So 
maybe there will be another blog post troubleshooting the newest version of 
chromium later on, but first, fixing mysql.

Browsering the man page for Upstart, we can see it's the init daemon and 
reads its configuration from the **/etc/init** directory. So that seems like 
a good place to look around for bad configurations. The man page from `man upstart` 
recommends looking into the 5(init) man page for details, so a quick `man 5 init` 
brings us to more documentation. 

One line in particular,  

    Users are able to manage their jobs using the standard initctl(8) facility.

stood out, and a quick look through there showed me the mysql process id changing 
rapidly when I ran `initctl status mysql`, having found the right daemon controlling
mysql, I checked the configuration:

	$initctl show-config mysql
	mysql
	  start on runlevel [2345]
	  stop on starting rc RUNLEVEL=[016]

Wondering what runlevel I was currently in led me to: 

	$ who -r
    	     run-level 2  2015-01-06 17:32

Well, this certainly explained why it kept restarting. I don't actually want 
mysql running on start up (and had disabled my other version's start up service 
a few weeks ago), so it was off to edit the run levels for me.

The /etc/rcn.d directories specify which scripts in /etc/init.d are enabled for 
run level n. So I checked it out and sure enough there was my disabled service
for my other mysql install:

	ls /etc/rc2.d/
	K80mysql.server

But there wasn't anything else in there for the mysql service (note, not mysql.server!).
I checked the other /etc/rcN.d/ directories but couldn't find anything. Weird.
So I ran a quick service check:

	ethan@Turing ~ $ sudo service mysql status
	mysql start/post-start, process 6958
		post-start process 6959
	ethan@Turing ~ $ sudo service mysql stop
	mysql stop/waiting

Well now that's just bizarre, and after calling service stop the logs stopped 
coming, and the `sudo sysdig -c fdcount_by proc.name "fd.type=file"` file to 0
for mysql. So I had stopped the issue, but I hadn't figured out what had caused
the problem. Why was the system trying to start mysql as a service on start up 
anyway? Especially if there wasn't anything in the /etc/rcN.d directory for it?

Well, the init scripts that run on startup and shutdown of the machine are actually
located in the /etc/init.d directory, so something had to have gone wrong here. 
I quickly checked to see if I could reproduce my log errors:

	ethan@Turing ~ $ sudo service mysql start
	ethan@Turing ~ $ sudo service mysql status
	mysql start/post-start, process 8047
		post-start process 8048
	ethan@Turing ~ $ sudo service mysql status
	mysql start/post-start, process 8122
		post-start process 8123
	ethan@Turing ~ $ sudo service mysql status
	mysql start/post-start, process 8122
		post-start process 8123
	ethan@Turing ~ $ sudo service mysql status
	mysql start/post-start, process 8192
		post-start process 8193
	ethan@Turing ~ $ sudo service mysql stop
	mysql stop/waiting

yup.

At this point, I thought about adding `service mysql stop` to my /etc/rc.local 
file to just stop the issue from happening. But that didn't seem like a good
way to fix the problem, so I pressed on and [found this] and followed through
with updating my overrides:

	echo "manual" >> /etc/init/mysql.override
	sudo reboot

And after my system booted back up?

	ethan@Turing ~ $ sudo service mysql status
	mysql stop/waiting

And my horrible broken mysql installation was fixed and no longer starting up at
runtime anymore! Amazing what reading the documentation can do for one's problems.



[found this]:http://upstart.ubuntu.com/cookbook/#disabling-a-job-from-automatically-starting
[this post]:http://askubuntu.com/a/296973/254629