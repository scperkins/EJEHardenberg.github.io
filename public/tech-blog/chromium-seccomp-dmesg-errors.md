### Chromium dmesg full of seccomp bugs fix

I've been getting into the habit of checking my `dmesg` log more often.
While [troubleshooting my mysql] errors the other week I noticed a lot 
of IO errors from my chromium installation (Chromium 37.0.2062.120) and
decided to look into it today.

I was getting similar [issues] to many others and had a log full of things
like this:

	[13225.732272] type=1701 audit(1421087245.965:678): auid=4294967295 uid=1000 gid=1000 ses=4294967295 pid=4664 comm="chromium-browse" reason="seccomp" sig=0 syscall=257 compat=0 ip=0x7f09c46f0720 code=0x50001
	[13225.732375] type=1701 audit(1421087245.965:679): auid=4294967295 uid=1000 gid=1000 ses=4294967295 pid=4664 comm="chromium-browse" reason="seccomp" sig=0 syscall=2 compat=0 ip=0x7f09c46f06c0 code=0x50001
	[13225.732383] type=1701 audit(1421087245.965:680): auid=4294967295 uid=1000 gid=1000 ses=4294967295 pid=4664 comm="chromium-browse" reason="seccomp" sig=0 syscall=2 compat=0 ip=0x7f09c46f06c0 code=0x50001
	[13225.732391] type=1701 audit(1421087245.965:681): auid=4294967295 uid=1000 gid=1000 ses=4294967295 pid=4664 comm="chromium-browse" reason="seccomp" sig=0 syscall=2 compat=0 ip=0x7f09c46f06c0 code=0x50001

After looking into it, the messages have something to do with the sandbox
environment in chrome. If you add the flag `--disable-seccomp-filter-sandbox` 
to the startup of chromium you'll not see the messages anymore, but you'll
also not be running a sandbox anymore. This is a bit of security issue, 
so you likely won't want to run without that flag. 

The easiest way to clean up the dmesg log is to tell the system logger to
send the chromium messages to their own log and not into the kernels. You 
can do this [pretty easily] on systems that use the syslog service 
accessible from `initctl`. On my system I had to restart the `rsyslog` but
besides that the setup was the same to fix the logging issue:

1. Create the file **/etc/rsyslog.d/30-seccomp.conf**
2. Add the code below this list to that file:
3. Restart the syslog via `initctl restart rsyslog` or `initctl restart syslog` 
(depending on your system)


	if $msg contains ' reason="seccomp"' and $msg contains ' comm="chrom' \
  		then -/var/log/chromium-seccomp.log
	& ~


Then you'll have those messages being logged to another area other than 
cluttering up your syslog!


[troubleshooting my mysql]:/tech/blog/mysql-upstart-without-purge
[issues]:https://productforums.google.com/forum/#!topic/chrome/vVZYVdKgGh0
[pretty easily]:http://askubuntu.com/a/425302/254629