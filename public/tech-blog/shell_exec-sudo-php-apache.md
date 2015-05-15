### PHP shell_exec, sudo, and remote servers 

When working with legacy, or even current software, it's not unusual to 
have a few scripts dedicated to accomplishing tasks. Often these can be 
things that simply rsync resources across nodes of a server, help 
migrate data between different data sources, back up code or data, or 
really anything you can think of. 

It's easy enough for a developer to get onto a machine and run their 
tools from a command line interface (CLI), but sometimes you don't want 
to be bothered by emails during the day when you're coding. For example 
let's say you've got a few scripts that connects to multiple servers 
and runs a command on each. It's easy to run a bash script from the 
CLI, but you'd save yourself grief if you exposed the tool to whoever 
is always emailing you asking for the task to be done! 

So, you think to yourself, Ah! I can write a quick script in PHP to do 
this! And you'd be right. Imagine something like this:

	<?php
	$logfile = '/tmp/util.log';
	$scriptpath = dirname(__FILE__) . '/script';
	if ($_SERVER['REQUEST_METHOD'] == 'POST'):
		//code to do param checking and such
		$exe = $scriptpath . $someparameters . ' >> ' . $logfile . ' 2>&1';
		$result = shell_exec($exe)
		if (is_null(result)): 
			//handle bad result
	else: 
		//display HTML form and such

And you've got a simple shell script that does something like this:

	#!/bin/bash
	source /some/path/to/a/listof/servers/to/connnect/to.sh
	for host in $SERVERS
	do
		ssh $host "cmd to do for a param $1"
		echo "Done! $1"
	done

While running the above script from the CLI will work, but should you 
attempt to run it from a server like apache or nginx, then you're going 
to hit error: 

	Could not create directory '/var/www/.ssh'.
	Host key verification failed.
	Done! <Whatever Params>

Being the good developer that you are, you realize that of course the 
web server can't ssh! It doesn't have an ssh folder or keys like your 
user. Let's assume you run as the root user when you do your CLI work 
([though you shouldn't]) so you decide that to run your script you 
simply need to sudo. Okay...

	$scriptpath = 'sudo sh ' . dirname(__FILE__) . '/script'; 

And when you go back to refresh the page what happens?

	sudo: sorry, you must have a tty to run sudo

Well darn. So now you think back to yourself and realize that the 
server doesn't really have a shell to work with. And sudo wants one 
of those. The simplest way around this is to disable the requiretty 
for the user. This is easily done via `visudo` and updating your web 
user's permissions:

	#Give permission to apache to run sh as root
	apache ALL=NOPASSWD: /bin/sh

	#Don't require a tty for apache
	Defaults:apache !requiretty

Once you've done this, then you'll be able to run your shell script. 
Here are some caveats to this though. 

1. You've given permission to apache to run a shell as root without 
   restriction 
2. apache no longer needs a terminal

This is *bad*. However, being the moderately inteligent developer you 
are, you know that you can [restrict the allowed commands]. So you 
update the sudoers file again with a quick `visudo`:

	apache ALL=NOPASSWD: /path/to/your/script

But until you update your PHP code you'll get the `sudo: no tty present and no askpass program specified` 
error message. Why? Because you're calling `sh`! 

	//no sh!
	$scriptpath = 'sudo ' . dirname(__FILE__) . '/script'; 

Make sure that your script file is `chmod +x` executable, then you're 
much safer. In addition, if you use safe_mode in php, you should 
set the `safe_mode_exec_dir` in your .ini file appropriately. 

Depending on your script, you may have a limited set of parameters. For 
example, say you're talking to `/etc/init.d/nginx` and you want to be 
able to restart the service from a form you built. So your form submits 
arguments like: `restart`, `stop`, `status`, or `start`. If that's the 
case, you can lock things down a bit more by using the wildcards found 
in the [sudo manual] or you can simply list each command individually.

Also, if you do open up your scripts as utilities, be mindful of who can 
access the pages. Lock them down with at least basic HTTP authentication, 
if possible, only expose such scripts to roles in the company that need 
that usage. Always follow the principle of least privilege and audit 
your systems regularly! When you grant a user the power to use your CLI 
tools, you give them a piece of your responsibility and take on more at 
the same time. Developers should strive to be lazy (in this case, 
reducing your effort in dealing with emails and distractions), but it's 
important to keep in mind that security and safety come first. 

[though you shouldn't]:http://askubuntu.com/a/16179
[restrict the allowed commands]:http://www.sudo.ws/man/sudoers.man.html
[sudo manual]:http://www.sudo.ws/man/sudoers.man.html#x57696c646361726473