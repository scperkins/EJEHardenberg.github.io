###Caching with Varnish for Api Servers. 

I've been working on creating a JSON API Server for Vermont's Green Up day for 
a while with some friends. We've managed to make a native iOS application as 
well as a web application for the client side, and the back end been a labor of
love for me: creating a JSON C API to service the various endpoints. 

The [C API] is blindingly fast, and performs amazingly consider I wrote everything
from scrach (http parsing, json parsing, etc, etc) and the entire application is
tailored to the needs of the data and client applications. We've done a good job
on [documentation] and on working as a team to solve the various issues and make
important decisions. To be honest, I take a degree of pride in it all.

Anyway, since the API server is designed as an abstraction interface over the data
(as pretty much all API servers are by definition), I focused on getting the data
quickly and reliably rather than doing any sort of caching. Why could I get away
with ignoring caching entirely while developing the API Server?

Because of [varnish], a web proxy that sits between your system and the rest of
the world. Handling caching according to cache control directives in HTTP headers
and a custom language called [vcl] that allows for some great control over the way
your cache is invalidated and some other great features (such as dropping cookies
-- though that wasn't used by our system).

[Cache Invalidation] is a hard thing. One of the [hardest] in Computer Science.
But, in this case, it's quite easy. Our system is designed to be read intensive
on most endpoints of the API, and write intensive on one. The resources that are
handled in a [REST]ful way are great because of their seperation. This means that
if I create a new resource for a [Report], then I only need to remove cached copies
of the reports, no other resources need to be touched. A clear seperation of parts
allows this, and I'll show you the vcl code that facilitates this soon. 

Not all resources are so clean cut though.  Both the [Comments] and the [Markers]
are intertwined with each other. This means that if I update one, then I need to
invalidate both of their cached resources. Simple isn't it? And vcl is able to 
support exactly this. Here's the configuration:

    sub vcl_recv {
        if ( req.request == "POST" || req.request == "PUT" ) {
            #Invalidate only the neccesary things per endpoint
            if ( req.url ~ "(?i)/api/comments" ) {
                    ban("req.url ~ (?i)/api/comments");
                    ban("req.url ~ (?)/api/pins");
            }
            if ( req.url ~ "(?i)/api/pins" ) {
                    ban("req.url ~ (?i)/api/comments");
                    ban("req.url ~ (?)/api/pins");
            }
            if ( req.url ~ "(?i)/api/heatmap" ) {
                    ban("req.url ~ (?i)/api/heatmap");
            }
            if( req.url ~ "(?i)/api/debug" ) {
                    ban("req.url ~ (?i)/api/debug");
            }
            #Don't cache POST or PUT (no sense in doing so)
            return(pass);
        }
    }

I've already explained what is being accomplished by this code, but let me just
say a little more: The `sub vcl_recv` is the procedure for when varnish recieves
a request. There's a [full list of vcl] configuration and procedures within varnish's
documentation. Next, if we are dealing with a [REST]ful update request (`POST` or `PUT`)
then we get ready to invalidate the cache. 

The `~` is the symbol to match the left hand side against the right hand side for 
a regular expression, in our case we are using the directive `(?i)` to use case-
insensitive matching against the url and our predefined API endpoints. These expressions
are simple enough to just match the url itself since our API schema itself is so simple. 

Finally, the `ban` [varnish function] actually performs the invalidation of the cache.
The term ban itself comes from the fact that the items in the cache that match whatever
expression is given to the function are banned from being within the cache anymore, and
hence invalidated. There's more information on [banning here]. Besides the ban itself,
the only other unexplained piece of the above code is the return(pass), which my
comment above it details sensibly enough. 

Varnish is a *very* powerful tool and for read intensive systems such as API servers
whose primary purpose is to provide abstraction on a database it can be used to 
mitigate the load experienced by a server itself. 


[documentation]:https://github.com/EJEHardenberg/GreenUp/tree/master/api
[C API]:https://github.com/EJEHardenberg/green-serv
[varnish]:https://www.varnish-cache.org
[vcl]:https://www.varnish-cache.org/docs/3.0/reference/vcl.html
[Cache Invalidation]:http://en.wikipedia.org/wiki/Cache_invalidation
[hardest]:http://martinfowler.com/bliki/TwoHardThings.html
[REST]:http://en.wikipedia.org/wiki/Representational_state_transfer
[Report]:https://github.com/EJEHardenberg/GreenUp/blob/master/api/readme.md#post-log-message
[Comments]:https://github.com/EJEHardenberg/GreenUp/blob/master/api/readme.md#submit-comments
[Markers]:https://github.com/EJEHardenberg/GreenUp/blob/master/api/readme.md#submit-pin
[full list of vcl]:https://www.varnish-cache.org/docs/3.0/reference/vcl.html#subroutines
[varnish function]:https://www.varnish-cache.org/docs/3.0/reference/vcl.html#functions
[banning here]:https://www.varnish-cache.org/docs/3.0/tutorial/purging.html