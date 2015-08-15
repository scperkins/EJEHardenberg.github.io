### Administration Gotcha's when proxying

**Warning. Blogging under irritation. You've been warned**

Everyone deals with Legacy systems and almost everyone who's ever had 
to do any system administration has ran into a server configuration 
that they didn't originally setup. A lot of the time these systems are
a cludge of multiple people's blood throughout the last 10 or more years.
Other times, let's be honest, they're just setup by idiots who've never
read a man page in their life\* or who didn't bother checking log files 
for anything odd before they ran out at 5:00pm sharp to get home to the
latest re-run of terrible-movie the show part 14 on HBO\*\*

I ran into something which may be a mix of these two while troubleshooting
some systems recently. [Everyone] knows to restrict access to sensitive 
information when you setup a server. And so you'll commonly see things like
this:

	<Location /server-status>
		SetHandler server-status
		Order Deny,Allow
		Allow from 127.0.0.1
	</Location>

Which is great. Now only people who have already compromised your box, or you, 
can get information about your server. This is a good thing (unless
you're compromised). But something which people love to do is use nginx to proxy.
After all, it's [recommended in the top hit for nginx vs apache in the 
"Using Nginx and Apache both" section] for pretty good reasons. But something 
else people do (which makes less sense), is to have both nginx 
_and_ apache running _on the same machine_. If your argument for using both 
systems is that nginx is better at static content, and apache better at heavy
processing, then you should probably understand that _if apache is taking all
the resources to work, it's going to affect nginx, and in that case, why don't
you just [shut off AllowOverride] and only use apache?_\*\*\*

Why am I mentioning this and the `server-status` handler above? Let me guide you
down the right path: What IP Address will nginx provide to apache when proxying?
If you answered **The ip of the client duh!** I would suggest you do two things.

1. [Click here](http://foaas.com/madison/dear reader/Ethan)
2. Keep reading. 

The correct answer is of course, `127.0.0.1` because nginx is running on your local 
system. And apache will see that local ip and correctly take the localhost as the 
incoming address. Of course, you view this as wrong, but how do you expect apache 
to know that it's being proxied to? It doesn't. _But_, we can fix that. First off,
you'll need [mod_rpaf] (or an [alternative]). Installing this is easy. 

1. Use your package manager to grab the `httpd-devel` package which includes the 
`apxs` command.
2. Download mod_rpaf (you can find a copy [here] or pull a release from github)
3. Open the tar file, or change into the root directory and run `apxs -i -c -n mod_rpaf-2.0.so mod_rpaf-2.0.c`
4. Create the configuration file <pre>#/etc/httpd/conf.d/mod_rpaf-2.0.so
LoadModule rpaf_module modules/mod_rpaf-2.0.so
RPAFenable On
RPAFsethostname On
RPAFproxy_ips 127.0.0.1
RPAFheader X-Forwarded-For</pre>
5. Restart apache.

Now apache will understand when someone sends headers along with `X-Forwarded-For` 
and `X-Host` that it's really supposed to be pretending that it got the request
for that IP and host directly and and not from whatever locally just came to it. 
This is all well and good, but you do need to update your nginx configuration to 
_set the headers in the first place_. As it's not going to do it by itself:

1. Open your nginx configuration and add in a couple lines to your proxying location:<pre>...
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header Host $host;
<pre>
2. Restart nginx 

That's it. You should now be able to look in your access logs (I know it might hurt
the log challenge, but really, do it) and see the real ip addresses coming in to 
apache and any `server-status` requests being denied. Don't get me wrong, server 
status is great. It shows useful information like server version, SSL library version,
what build you're using, how much traffic you're dealing with, and _every ip address
connected to your system!_. Which is all, obviously, public information you want to share 
with everyone.\*\*\*\*

While you're in your configuration, you may also consider shutting off your 
[server's signature] as well. That is, as long as it's not past 5pm and your 
re-run isn't calling you.


<small>\* For the love of god, read a man page or some documentation
before you put something in production</small><br/>
<small>\*\* Really. Check your log files when you turn something
on</small><br/>
<small>\*\*\* Pretty sure I saw a benchmark a while ago showing that
Apache performed just as well as nginx when AllowOverride was
off</small><br/>
<small>\*\*\*\* If you want to get hit by exploits specific to your server version</small>

[Everyone]:http://foaas.com/everyone/Anyone%20who%20reads%20manpages
[recommended in the top hit for nginx vs apache in the "Using Nginx and Apache both" section]:https://anturis.com/blog/nginx-vs-apache/
[shut off AllowOverride]:http://www.eschrade.com/page/why-you-should-not-use-htaccess-allowoverride-all-in-production/
[mod_rpaf]:https://github.com/gnif/mod_rpaf
[alternative]:http://massivescale.blogspot.com/2013/10/alternatives-to-modrpaf.html
[here]:http://drupion.com/sites/default/files/mod_rpaf-0.6.tar_.gz
[server's signature]:http://ask.xmodulo.com/turn-off-server-signature-apache-web-server.html
