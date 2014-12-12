## Proxies, Paranoia, and resolv.conf

### Having some weird issues...

I've been having this weird issue lately, well, actually a couple of 
weird issues. Mainly the following for the last few months or so:

- instead of 404's I get a weird not available page 
- instead of 404's on an https page, I get a privacy error
- my internet likes to stop working after these 404's on occasion

So, if I lost connection and tried to go anywhere over HTTPS, I'd see this 
lovely image:

<img src="/images/tech-blog/sec.se.jpg" width="600px" />

And if I tried over regular HTTP I'd see:

<img src="/images/tech-blog/sec.se.404.jpg" width="600px" />

### Enough is enough

So the other day I was looking at some funny pictures on the internet and 
happened to lose connection. This was when I discovered that my HTTPS 
connections were routing themselves, on 404's, to a certificate claiming 
to be from [hackvt.com]. Finding this rather odd, I inspected the certificate 
and compared it to the one which a friend could view.

Same certificate. This should have been a dead ringer for my problem, but 
instead I ran off the notion that before, when I had [upgraded chromium], 
I had also been fooling around with the `--proxy-server`, so maybe something 
had gone wrong there.

I checked my settings, my gnome settings and config. Opened up [iftop] and 
tried to figure out where my connection was going and why. I pinged my friend 
Phelan, and together we slodged through the output of `env`, `netstat`, /etc/hosts, 
and I even peered through my `service --status-all` looking for malicious 
programs.

We chatted back and forth trying to figure things out. Finally, I ran a wget and
noticed this:

	$ wget https://sec.se
	--2014-12-12 14:50:57--  https://sec.se/
	Resolving sec.se (sec.se)... 162.209.42.221
	Connecting to sec.se (sec.se)|162.209.42.221|:443... connected.
	ERROR: cannot verify sec.se's certificate, issued by `/C=US/ST=Arizona/L=Scottsdale/O=GoDaddy.com, Inc./OU=http://certs.godaddy.com/repository//CN=Go Daddy Secure Certificate Authority - G2':
	  Unable to locally verify the issuer's authority.
	ERROR: no certificate subject alternative name matches
		requested host name `sec.se'.
	To connect to sec.se insecurely, use `--no-check-certificate'.

After checking the IP address a few times and convincing myself that it was 
the real [hackvt.com] server. It finally occured to me.

"Oh, it's RESOLVING the address from that ip."

And from there it was one step into `/etc/resolv.conf` to find my issue:

    search hackvt.com

<small>In the picture I've already commented out the two offending lines</small>
<img src="/images/tech-blog/sec.se.derp.png" width="600px">

This was when my memory came in, and I recalled that at the first hackvt event I 
had gone to, we had needed to add the resolv to get _something_ to work. I don't
remember what, but I do know that that was 3 years or so ago. And once I took out 
the two offending lines and ran `/etc/init.d/networking restart` that I then got 
the best 404 of my life:

	$ wget https://sec.se
	--2014-12-12 15:42:58--  https://sec.se/
	Resolving sec.se (sec.se)... failed: Name or service not known.
	wget: unable to resolve host address `sec.se'

### Two birds with one stone

Thinking about how my internet sometimes kicked itself when I had a lot of tabs 
open and then got a 404, I opened up the [documentation on resolv.conf] out of 
curiousity and found a nice surprise in the search section:

<blockquote>
"Note that this process may be slow and will generate a lot of network traffic 
if the servers for the listed domains are not local, and that queries will time 
out if no server is available for one of the domains."
</blockquote>

And suddenly, why I lost internet on 404's all the time was made clear to me. So, 
sorry internet, I was likely a bad netizen for a few years and I bet there's a 
sysadmin out there who is **really** confused why someone was trying to use his 
web server as a DNS.


[hackvt.com]:http://hackvt.com
[upgraded chromium]:/tech-blog/upgrading-chromium-33-to-37
[iftop]:http://www.slashroot.in/linux-iptraf-and-iftop-monitor-and-analyse-network-traffic-and-bandwidth
[documentation on resolv.conf]:http://linux.die.net/man/5/resolv.conf