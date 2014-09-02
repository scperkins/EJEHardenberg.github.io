###Using Directors in Varnish

Quite frankly, I love [Varnish] and am quite happy with the level of control and
possibilities given by the VCL files. I've [blogged before] about how [XenonApps]
uses Varnish for our [Green Up App]'s API Server, but today I'm going to talk 
about how we handle crashes and making sure that the system is available even
when we're having problems.

First off, the concept of a load balancer will be familiar to anyone whose ever
used [AWS] services before. However, at XenonApps, we're not using AWS, so we
have our own way of dealing with it. A [Load Balancer] is a pretty simple concept.
It sits in front of other applications and directs incoming requests to different
"backends". In our case, our backend is the [C API Server], and our load balancer
is Varnish.

That's right kids. Varnish.

Varnish provides more than just a cache by allowing you to define [Directors] to
link multiple back ends together. These back ends can be running on different
ports, machines, or be entirely different applications all together. Here's how
we've setup our Green Up backends setup:

    backend default {
        .host = "127.0.0.1";
        .port = "30000";
        .probe = {
                .url = "/api/";
                .interval = 10s;
                .timeout = 2s;
                .window = 5;
                .threshold = 3;
        }
	}
	backend backup {
        .host = "127.0.0.1";
        .port = "30001";
        .probe = {
                .url = "/api/";
                .interval = 10s;
                .timeout = 2s;
                .window = 5;
                .threshold = 3;
        }
	}
	backend backup2 {
        .host = "127.0.0.1";
        .port = "30002";
        .probe = {
                .url = "/api/";
                .interval = 10s;
                .timeout = 2s;
                .window = 5;
                .threshold = 3;
        }
	}
	director backup_director round-robin {
        {
                .backend = default;
        }
        {
                .backend = backup;
        }
        {
                .backend = backup2;
        }
	}
	sub vcl_fetch {
        set req.backend = backup_director;
	}


Now, this is a pretty simple setup to understand, but let me just go over it and
mention a gotcha that got me. 

First off, we define each backend, this is standard varnish configuration. If 
you're doing something that's facing the web you've likely got something like this:

	backend default {
		.host = "127.0.0.1";
		.port = "8000";
	}

or something similar to how you've setup your server ports. The piece you might
not recognize is the `.probe` configuration. Probes are what AWS (and the rest of the world)
call health checks. They're Varnish's way of determining if the backend is still
running or not. The `interval` is how often Varnish will check the backend's health status.
`.timeout` is how long the backend has to respond to a request from varnish to the `url`.
If you've ever read up on the TCP protocol, or most network protocols, you'll remember
something called a "sliding window". In Varnish, the `window` parameter to the probe
indicates how many requests Varnish will remember. If `threshold` number of checks
are healthy within the last window, then Varnish will consider the backend operational.

In case you're wondering, `/api/` is the Heartbeat of the API server. If you've ever
wondered why API writers create these seamingly useless echoing of the current time, 
this is one of the many reasons why.

Next in our configuration we get to the `director`, this is running the show. Varnish
has two different types of directors, the `round-robin` and `random`. Round robin
will simply deliver requests to the backends in sequence. Looping around to the previous
once we've run out of backends. It's a fairly common strategy and you'll find it
in [Process Scheduling, Network packet schedeling, and a lot of other places].

And last, but not least, we tell varnish to actually use our director by updating
our `vcl_fetch` method to set the backend to use the director. This is where I
got bit before. I did everything but this step and ran into [the same problem as this guy].

Once all this was setup, I restarted Varnish and ran my backends. Opening up `varnishlog`
to make sure. If you're is working like mine, you'll see something similar to this:

    0 Backend_health - backup2 Still healthy 4--X-RH 5 3 5 0.000639 0.000811 HTTP/1.1 200 OK
    0 Backend_health - backup Still healthy 4--X-RH 5 3 5 0.000580 0.000657 HTTP/1.1 200 OK
    0 Backend_health - default Still healthy 4--X-RH 5 3 5 0.000670 0.001173 HTTP/1.1 200 OK

And it's really that easy.


Now that you've got your backends set up to be healthy you might want to enable 
[grace and saint mode]. This will allow you to serve stale content while a backend
is unhealthy. Useful! 



[Varnish]:https://www.varnish-cache.org/
[blogged before]:http://ethanjoachimeldridge.info/tech-blog/varnish
[XenonApps]:http://xenonapps.com
[Green Up App]:https://itunes.apple.com/us/app/green-up-vt/id860271437?ls=1&mt=8
[AWS]:http://aws.amazon.com/
[Load Balancer]:http://en.wikipedia.org/wiki/Load_balancing_(computing)
[C API Server]:https://github.com/EJEHardenberg/green-serv
[Directors]:https://www.varnish-cache.org/docs/2.1/tutorial/advanced_backend_servers.html
[the same problem as this guy]:https://www.varnish-cache.org/lists/pipermail/varnish-misc/2011-May/020566.html
[Process Scheduling, Network packet schedeling, and a lot of other places]:http://en.wikipedia.org/wiki/Round-robin_scheduling
[grace and saint mode]:https://www.varnish-cache.org/docs/3.0/tutorial/handling_misbehaving_servers.html#tutorial-handling-misbehaving-servers