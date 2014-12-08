### Your own Mailing List

#### Quick why and what

If you're like me, your email inbox is like a second home. Information about 
friends, events, and all sorts of things come filtering through. A lot of the 
time you might have a designated group of friends whom you share a lot of links 
with. If you use [gmail] or any decent webmail client you're likely familiar 
with the concept of lists. 

Within your inbox, you can add a list of users into a group that you can then 
email easily. Within gmail, these groups expand out into the numerous users 
you want to talk to, you write an email, and off it goes. Welcome to the  
information age. However, sometimes people forget to hit 'reply-all', 
or they want to share information too, but they only sent it to you. So you forward 
it out to everyone on your group and then proceed to enjoy the thought catalog 
coming your way. 

But if you're like me, you'd prefer if _everyone_ could share a group. So that 
everyone can email the one address and instantly everyone who cares to be on 
the mailing list is enjoying it. In this blog post, I'm going to show you how to 
set up your own mailing list. 

#### What you'll need

- A server open to the web
- Linux running on said webserver (debian is what these instructions will be for)
- about 15 minutes or so and some patience

#### Postfix? Sendmail? What do I use?!

When setting up an [SMTP] typically one uses [sendmail] or [postfix] and if you're
lucky, one might even come preinstalled on your distro. For me, I wanted a mail 
server that could use a whitelist and blacklist without too much of a hassle. 
Since sendmail [doesn't really support that], I installed postfix instead since 
[it does].

#### Install postfix

Installing postfix is easy, on debian just use `apt`:

    sudo su
    aptitude install postfix

It will ask you a few questions during the configuration, one of the important 
ones to note is when you're setting up your FQDN (Fully Qualified Domain Name). 
It should be set to the output of `hostname --fqdn` on your machine. Also, when 
asked which configuration option you'd like, set it to "Internet Site" as you'll 
be wanting to recieve and sendmail from your machine to facilate the mailing list.

#### Configuring postfix

Next, you need to configure. This can be done by checking out two files: 

1. /etc/postfix/main.cf
2. /etc/postfix/master.cf

**main.cf** is the file you'll want to spend some time on. If you want to 
understand the file, I suggest [reading the documentation]. It's rather helpful 
and answers a lot of questions you might have right off the bat. The configuration 
that I changed was as follows: 

	myhostname = your.domain.here.com
	mydestination = your.domain.here.com, $myhostname, localhost.info, localhost, mail.your.domain.here.com, mail.$hostname
	mynetworks_style = host
	notify_classes = bounce, resource, software
	smtpd_recipient_restrictions = check_client_access hash:/etc/postfix/client_checks, check_sender_access hash:/etc/postfix/sender_checks, reject_unauth_destination

The last line of the configuration is to setup [a whitelist]. Note that the linked 
blogpost does not include the `reject_unauth_destination`, this was neccesary because 
otherwise you're going to get a lot of errors like this in your log:

	postfix/smtpd[1435]: fatal: parameter "smtpd_recipient_restrictions": specify at least one working instance of: check_relay_domains, reject_unauth_destination, reject, defer or defer_if_permit

Taking note of `/etc/syslog.conf` you'll want to be sure where your mail server 
is logging to. Then the handy dandy: `tail -n 20 /var/log/mail.*` can help you 
figure out what's going wrong if anything does.

#### Setting up the mailing list

First, make a username for the alias you'll use. Let's pretend you're setting up 
a mailing list for your family to share vacation pictures and have decided that 
your mailing list will be called "vacations" (creative I know).

    useradd vacations
    passwd vacations #enter a password

    vi /etc/aliases #if you're using vim, use nano if you'd like, or emacs or whatever

Once the aliases file is open simply add in a section like this near the bottom:

    #/etc/aliases

    #... bunch of stuff

    vacations:
      mom@domain.com
      dad@domain.com
      brother@domain.com
      sister@domain.com
      #etc etc list all the email addresses you want in here
      #Note, if you're using a whitelist then make sure they're included

Then run the command to refresh your aliases:

    newaliases
    postalias /etc/aliases #important!
    /etc/init.d/postfix reload

If you're using [a whitelist] make sure to create the databases for your mail 
server by running the following:

	#You'll need to make the *_checks files first obviously, see the link above
    postmap /etc/postfix/client_checks
	postmap /etc/postfix/sender_checks
	/etc/init.d/postfix reload

Once this is all setup it's time to setup your DNS records. Go into your providers 
configuration and look for MX records. For some providers they may already have 
FAQ's or tutorials on setting up your mailserver to relay to theirs. But a quick 
and dirty approach is to simply edit the MX record to point directly to your 
server's IP address.

Next, if you're running a firewall you'll want to punch a hole in it for your 
mail server to talk through. If you're using [ufw] all you need to do is run 
the command: `ufw allow smtp` and you should end up with a status like this:

	$ufw status
	Status: active
	
	To                         Action      From
	--                         ------      ----
	22                         ALLOW       Anywhere
	80                         ALLOW       Anywhere
	443/tcp                    ALLOW       Anywhere
	25/tcp                     ALLOW       Anywhere
	22                         ALLOW       Anywhere (v6)
	80                         ALLOW       Anywhere (v6)
	443/tcp                    ALLOW       Anywhere (v6)
	25/tcp                     ALLOW       Anywhere (v6)

Once this is done, you'll want to test the mailing list. Go back to your aliases 
file and comment out (use a #) everyone but you and a [test email] and write an 
email to your new alias: "vacations@domain.com". Before you send it, tail the 
log on your server with: `tail -f /var/log/mail.info`

If you don't see something like 

	postfix/smtpd[1520]: connect from unknown[x.x.x.x]
	postfix/smtpd[1520]: warning: support for restriction "check_relay_domains" will be removed from Postfix; use "reject_unauth_destination" instead
	postfix/smtpd[1520]: 640932615C2: client=unknown[x.x.x.x]
	postfix/cleanup[1524]: 640932615C2: message-id=<someidofthemessagesender@mail.gmail.com>
	postfix/qmgr[1460]: 640932615C2: from=<testuser@yourhost.com>, size=3422, nrcpt=1 (queue active)
	postfix/cleanup[1524]: 7EDEB2615C3: message-id=<someidofthemessagesender@mail.gmail.com>
	postfix/qmgr[1460]: 7EDEB2615C3: from=<testuser@yourhost.com>, size=3568, nrcpt=2 (queue active)
	postfix/local[1525]: 640932615C2: to=<vacations@yourdomain.com>, relay=local, delay=0.12, delays=0.11/0.01/0/0, dsn=2.0.0, status=sent (forwarded as 7EDEB2615C3)
	postfix/qmgr[1460]: 640932615C2: removed
	postfix/smtpd[1520]: disconnect from unknown[x.x.x.x]
	postfix/smtp[1526]: 7EDEB2615C3: to=<test@cock.li>, orig_to=<vacations@yourdomain.com>, relay=mail.cock.li[x.x.x.x]:25, delay=0.15, delays=0/0.01/0.07/0.07, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued as 97A5B26116B)
	postfix/smtp[1527]: 7EDEB2615C3: to=<youremail@domain.com>, orig_to=<vacations@yourdomain.com>, relay=gmail-smtp-in.l.google.com[x.x.x.x]:25, delay=0.43, delays=0/0.02/0.06/0.35, dsn=2.0.0, status=sent (250 2.0.0 OK 1418057717 n77si43908260q1d.64 - gsmtp)
	postfix/qmgr[1460]: 7EDEB2615C3: removed

then you'll want to check your .err,.info, and .warn logs, a quick way to do so 
is to run `tail /var/log/mail.*` and look at the timestamps to determine where 
the mail you sent was.

Once you've got test emails working you'll want to uncomment the real email 
addresses you'd like to use and remove the test ones. After this, it's happy 
emailing and your friends and you should be able to share information with 
everyone at once with a single address.


#### A few gotchas

Mail server's can suck to debug sometimes, this is mainly because they're out in 
the wild wild west (www) and lots can go wrong. Here's a few issues you might 
run into and their fixes:

##### My email keeps getting sent back to me!

If you're getting emails with something like: "[Relay access denied]" then you 
need to take a look at your DNS settings and make sure they're pointing to your 
server. If they are, try asking your DNS provider about MX records and the error.

##### I send the email, it hits a test address, but doesn't show up in my own inbox on gmail

In this case, you might be hitting [this problem with postfix], in which case 
there's not much to be done, but trust that your email is being delivered. On 
the bright side, you'll see the email if someone replies back to your list. So 
all is well.

##### Problems installing postfix with apt-get? 

If you're using `apt-get` and have funny repositories you might run into some weird 
glitches where the the machine yells about not being able to do anything, just try
out `aptitude` and say no to the first option then agree to one that downgrades 
incompatible versions of other software.

##### aliases.db is older than source file?

    postfix/smtpd[1307]: warning: database /etc/aliases.db is older than source file /etc/aliases

If you get the above error, just run `newaliases` and you should be all set

##### No client.db or sender_check.db ?

    postfix/smtpd[1311]: fatal: open database /etc/postfix/client_checks.db: No such file or directory
    postfix/smtpd[1352]: fatal: open database /etc/postfix/sender_checks.db: No such file or directory


You'll get this error if you specify `check_client_access hash:/etc/postfix/client_checks` 
in the `smtpd_recipient_restrictions` block and haven't ran the `postmap /etc/postfix/client_checks` 
command yet. You'll get a similar one for the sender_checks if you don't follow 
the full instructions in the [whitelist blogpost].

##### smtpd check_relay_domains not set in smtpd_recipient restrictions

	postfix/smtpd[1386]: fatal: parameter "smtpd_recipient_restrictions": specify at least one working instance of: check_relay_domains, reject_unauth_destination, reject, defer or defer_if_permit

If you get this error message, all you need to do is read it and follow what it tells 
you to do (add `reject_unauth_destination` to the `smtpd_recipient_restrictions` list) in 
/etc/postfix/main.cf. I'd recommend using "reject_unauth_destination" since you'll
get the following warning if you use "check_relay_domains":

    postfix/smtpd[1505]: warning: support for restriction "check_relay_domains" will be removed from Postfix; use "reject_unauth_destination" instead


##### Credit where credit is due! 

This blogpost drew heavily from the [documentation] as well as the new tutorial 
on creating a mailing list [here] which provides a quick reference point for the 
gist of setting up aliases within your system.






[SMTP]:http://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
[gmail]:http://mail.google.com
[sendmail]:http://www.sendmail.com/sm/open_source/
[postfix]:http://www.postfix.org/
[doesn't really support that]:http://forums.fedoraforum.org/showthread.php?t=72511
[it does]:http://www.linuxlasse.net/linux/howtos/Blacklist_and_Whitelist_with_Postfix
[reading the documentation]:http://www.postfix.org/BASIC_CONFIGURATION_README.html
[a whitelist]:http://www.linuxlasse.net/linux/howtos/Blacklist_and_Whitelist_with_Postfix
[ufw]:https://help.ubuntu.com/community/UFW
[test email]:https://www.guerrillamail.com
[this problem with postfix]:http://serverfault.com/a/255564/220819
[Relay access denied]:https://www.penpublishing.com/Support/EmailErrors/UnderstandingEmailErrors/#554
[whitelist blogpost]:http://www.linuxlasse.net/linux/howtos/Blacklist_and_Whitelist_with_Postfix
[documentation]:http://www.postfix.org/BASIC_CONFIGURATION_README.html
[here]:http://www.tldp.org/LDP/LGNET/issue72/teo.html