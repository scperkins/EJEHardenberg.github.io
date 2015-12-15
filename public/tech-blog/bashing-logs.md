### Watching logs, an adventure in bashing

A few of my friends have said they enjoy blog posts that go into the 
thought process behind code. Like when looking at [string performance 
in python] or [troubleshooting a weird bug with strace]. So today I 
want to walk through a really simple bash script that was fun to make 
and interesting to think about.

In the usual course of any programmers life, if they take a project 
from start to finish, there'll be a lot of log files. Whether for 
monitoring, or for checking progress of batch updates and other 
similar tasks. The typical command every developer keeps in their 
pocket is this one:

	tail -f /var/log/myapplog.log

And this does the job for when you're monitoring some weird bug 
locally and have increased your logging. If you're running some batch 
process that logs to a file you might feel your eyes glaze over as you 
`tail` and see your 359th line of

	[INFO] Random Batch Process X Done, Starting Process Y!" 

You might even start working on something else while you wait if 
you're a productive person. But chances are that once you do it won't 
be until you flip to your terminal a while later that you realize you 
can get on with whatever other process was blocked by your batch 
process.

The obvious solution is to monitor your log and notify yourself 
somehow when the log file has stopped updating. So, how do you do 
this? I'll cover two approaches, the first uses `diff` the other uses 
`tail`. I first used `diff` because I thought of the process as 
checking the difference between the state of the log at different 
points in time. The first thing we need to do to build our state then 
is to capture the log file at time T! This is easy to do with bash:

	tail mylog.log > capture.1
	sleep 1
	tail mylog.log > capture.2

The above will grab the log file's last 10 lines of code (the default 
for `tail`) and place them into our two capture files. Waiting a 
second inbetween captures. Now that we have two files we can simply 
`diff` them:

	diff capture.1 capture.2 
	# or diff capture.*

and we'll get a bunch of lines of output showing us the difference in 
the two files. This is nice and all, but a bunch of lines isn't the 
easiest thing to deal with in bash. So instead we can check the manual 
for diff and see that there is an option to get a much simpler output, 
`-q`, or `--brief`, which only outputs if the two files are different 
and not their actual differences. 

	> diff -q capture.*
	Files capture.1 and capture.2 differ #or nothing if they do not

Using this we can simply check the output of diff as a string and act 
on this in bash using a simple `if`:
	
	DIFFCMD=`diff -q capture.1 capture.2`
	if [[ "Files capture.1 and capture.2 differ" == "$DIFFCMD" ]]; then
		#do something when they differ
	else 
		#do something when they don't
	fi

Of course, to _watch_ a log implies that we're keeping an eye on it, 
and so we need to loop our `diff`ing of the file. This is pretty easy 
to do in bash, we simply need a sentinal and a loop:

	KEEPDIFFING=1
	while [[ $KEEPDIFFING -eq 1]]; do 
		# If statement and updates to KEEPDIFFING
	done

With these pieces, we can easily make a generalized bash script that 
can monitor any of our logs:

	#!/bin/sh

	if [ $# -eq 0 ]; then
		echo "Usage: ./monitor.sh /my/log/file.log [sleep time (s)]"
		echo "Will output a dot for each second monitored that there are no changes"
		echo "Will stop script once no changes are detected to log file"
	fi

	if [ $# -eq 1 ]; then
		LOGFILE=$1
	fi

	SLEEPTIME=1 #Default sleep time
	if [ $# -eq 2 ]; then
		LOGFILE=$1
		SLEEPTIME=$2
	fi

	echo "Monitoring $LOGFILE"

	AFILE="/tmp/monitor.log.a"
	BFILE="/tmp/monitor.log.b"
	KEEPDIFFING=1

	echo "Please wait, setting up monitoring"
	tail $LOGFILE > $AFILE
	sleep 1
	tail $LOGFILE > $BFILE
	echo "Monitor files ready"
	echo "Checking logfile differences every $SLEEPTIME second(s), will stop script once no changes are detected"
	echo -n "Start at: " && date

	while [[ $KEEPDIFFING -eq 1 ]]; do
		DIFFCMD=`diff -q $AFILE $BFILE`
		if [[ "Files $AFILE and $BFILE differ" == "$DIFFCMD" ]]; then
			echo -n "." #Progress indicator that the script is running.
		 	KEEPDIFFING=1;
		 	tail $LOGFILE > $AFILE
		 	sleep $SLEEPTIME;
		 	tail $LOGFILE > $BFILE
		else
			echo "No update to log file in last $SLEEPTIME second(s), stopping script"
			echo -n "Stopped at: "
			date
			KEEPDIFFING=0
		fi 
	done

Now this will work fine for monitoring a _single_ logfile. But what 
about if we need to monitor more than one at a time? Or if multiple 
users on a server are all trying to keep an eye on it? Well, we could 
use random or dated filenames. But eventually we'll hit that one edge 
case where we accidently overwrite someone elses temporary capture 
file. So we need to switch to a different method, and this is the 
second approach I mentioned above, using `tail`.

Our initial reason for not using tail was because logically, using the 
`diff` tool to find _diff_erences just makes sense. But if we think of 
the last _n_ lines of a log file as being just a string, than we can 
see that we can compare a string just as easily (more so even) than a 
file capturing the state. Instead of capturing the differences in a 
temporary file, we can assign them to string variables:

	CAPTURE1=`tail mylog.log`
	sleep 1
	CAPTURE2=`tail mylog.log`

Then compare them with bash like any other string:

	if [[ "$CAPTURE1" == "$CAPTURE2" ]]; then 
		#Do something if they match
	else 
		#Do something if they don't
	fi

We can therefore modify our script to not use any temporary files and 
be concurrently available for all users:

	echo "Please wait, setting up monitoring"
	ACAPTURE=`tail $LOGFILE`
	sleep 1
	BCAPTURE=`tail $LOGFILE`
	echo "Monitor files ready"
	echo "Checking logfile differences every $SLEEPTIME second(s), will stop script once no changes are detected"
	echo -n "Start at: " && date

	while [[ $KEEPDIFFING -eq 1 ]]; do
		if [[ "$ACAPTURE" != "$BCAPTURE" ]]; then
			echo -n "." #Progress indicator that the script is running.
		 	KEEPDIFFING=1;
		 	ACAPTURE=`tail $LOGFILE`
		 	sleep $SLEEPTIME;
		 	BCAPTURE=`tail $LOGFILE`
		else
			echo "No update to log file in last $SLEEPTIME second(s), stopping script"
			echo -n "Stopped at: "
			date
			KEEPDIFFING=0
		fi 
	done

The above update will work, but you may have already noticed that we 
are now using both a sentinel with `KEEPDIFFING` and a conditional. We 
can simplify the code a little bit and remove the sentinel since we 
only want to run the `else` branch once we're ready to exit the loop 
anyway. So we can simplify the code down to:

	#!/bin/sh

	if [ $# -eq 0 ]; then
		echo "Usage: ./monitor.sh /my/log/file.log [sleep time (s)]"
		echo "Will output a dot for each second monitored that there are no changes"
		echo "Will stop script once no changes are detected to log file"
	fi

	if [ $# -eq 1 ]; then
		LOGFILE=$1
	fi

	SLEEPTIME=1 #Default sleep time
	if [ $# -eq 2 ]; then
		LOGFILE=$1
		SLEEPTIME=$2
	fi

	echo "Monitoring $LOGFILE"

	ACAPTURE="A"
	BCAPTURE="B"
	echo "Checking logfile differences every $SLEEPTIME second(s), will stop script once no changes are detected"
	echo -n "Start at: " && date

	while [[ "$ACAPTURE" != "$BCAPTURE" ]]; do
		echo -n "." #Progress indicator that the script is running.
		ACAPTURE=`tail $LOGFILE`
		sleep $SLEEPTIME;
		BCAPTURE=`tail $LOGFILE`
	done

	echo "" #move down from the dots
	echo "No update to log file in last $SLEEPTIME second(s), stopping script"
	echo -n "Stopped at: "
	date
	
Which is easy to read and understand. In the above script we're just 
spitting out the `date` that the script stopped running at. But if 
you wanted to be notified, you could use something like 

	notify-send "System Alert" "The process you were waiting for is done!"

If you're running this on your local machine and have `notify-send` 
installed. If this is a remote machine that has an SMTP program 
installed you could send an email with the `mail` command:

	echo "The process is done" | mail -s "System Alert" user@myhost.com

just place this at the end of the script and you'll be all set! It's 
easy and simple to combine the tools that the linux command line gives 
you to create useful scripts that can help you in your every day life 
as a developer. 

[string performance in python]:/tech-blog/string-interpolation-vs-addition-performance
[troubleshooting a weird bug with strace]:/tech-blog/strace-adventure