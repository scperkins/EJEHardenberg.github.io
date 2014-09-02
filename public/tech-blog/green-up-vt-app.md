###A little information the app side of Green Up VT

It's no secret that I've blogged about the [Green Up App] a [couple] times [before].
Myself and the rest of the [XenonApps] crew had quite the weekend. After contacting
the [Green Up Organization] we started to get some [press][] [in][] [the][] [local][] [news]
about it. It was pretty exciting, and  with the pressure on we wanted to make sure 
everything performed well. 

So Friday Night, [Josh Dickerson] and I sat down and started migrating the applications
that XenonApps wrote to our production database. We had a development server that
had been serving us faithfully, but since we figured the load might be bigger than
anticipated with all the press, we set everything up, and I configured Varnish 
and the other API related services like I had [before]. We had some troubles with
getting the Apache configuration to stick, but after beating at it until 2am we 
finally got it. 

Saturday morning I was up by 8am and at Josh's apartment, joined by our iOS developer
[Anders], monitoring the status of the [API server] and making sure that the web
[dashboard] and web app [client] functioned properly. Around 9am or so we were
noticing some small bugs in the error logs from the Administrative dashboard we 
had made. Something was up with the server configuration.

After 10 or so minutes of attempting to trace the mis-configuration and failing, we 
made the executive decision to swap the domain names to point to our development
server again. Once we did that all of those errors disappeared. We were running
on a smaller server, but throughout the entire day it held up. 

Our use of a small, cheap, server with 256MB of Ram (your phone has more!) as the 
+
server running the entire greenup.xenonapps application sounds rediculous. But hey,
our tagline on our site doesn't include efficient for nothing! The Dashboard and 
clients are light. They're just simple HTML, some Javascript, and a small PHP
script to get around some [XSS] issues we had early on. The biggest resource hog
was the API server (As expected), however the API server, as [noted in the readme]
is simple and speedy. Using about 13-36% of the CPU on the small box depending on
the load at the time, it's reasonably lightweight for something servicing over 100 
clients connecting and requesting data all at  once. 40mb in resources is great
for that (Keep in mind, 40Mb for ALL 100+ clients, not for each request as you
might see with something like WordPress or your typical php framework).

The applications we made for Green Up were the following:

- iOS App
- API Server
- Web Client for Android and other smart phones
- Dashboard for the world to follow along
- Admin dashboard for GreenUp and ourselves to administer and monitor data

My role within the project was primarily focused on the API Server itself, constructing
the [documentation] of the API so that the other applications could use the data
without needing to know the internals of how they retrieved it (that is what an API
is after all!). We originally used the [GAE] for the program, but when I performed
a simple load test on it: I managed to seg-fault python. So, I took my documentation
and used it as a specification for writing the C version of the API. It was a great
experience. Programming in C is one of my favorite things to do, and getting to
right not only the JSON and HTTP handling methods, but also interact with the low
mySQL C API was just downright fun. You can read the commit messages on the [API server]'s
repository if you want all the details. 

Overall, Green Up was a great success, not only for the local environment, but also
as a milestone in [XenonApps]'s life. As this marks our first successful deployment
of an application. We've already identified some areas we want to improve in our 
client applications, and I've got a little bit of refactoring for the API itself
to perform even better next year. 


[Green Up App]:https://itunes.apple.com/us/app/green-up-vt/id860271437?ls=1&mt=8
[couple]:ethanjoachimeldridge.info/tech-blog/varnish
[before]: ethanjoachimeldridge.info/tech-blog/varnish-directors
[XenonApps]:http://www.xenonapps.com
[Green Up Organization]:http://www.greenupvermont.org
[press]:http://digital.vpr.net/post/green-day-theres-app
[in]:http://www.wcax.com/story/25394218/new-green-up-day-app
[the]:http://learn.uvm.edu/blog-vermont/uvm-students-and-alumni-develop-green-up-vermont-app
[local]:http://rutlandherald.com/article/20140502/THISJUSTIN/705029880
[news]:http://www.timesargus.com/article/20140502/THISJUSTIN/705029881
[Josh Dickerson]:http://www.joshuadickerson.com/
[Anders]:https://github.com/popwarfour
[API server]:https://github.com/EJEHardenberg/GreenUp/tree/master/api
[dashboard]:http://greenup.xenonapps.com/dash/
[client]:http://greenup.xenonapps.com/client/
[XSS]:http://en.wikipedia.org/wiki/Cross-site_scripting
[noted in the readme]:https://github.com/EJEHardenberg/green-serv
[documentation]:https://github.com/EJEHardenberg/GreenUp/tree/master/api
[GAE]:https://developers.google.com/appengine/?csw=1