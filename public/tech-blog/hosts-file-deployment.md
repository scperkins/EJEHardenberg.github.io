My coWorkers and I were trying to determine a way to take a production
system that isn't maintained under version control, and swap it out with
the new system that needs to be deployed with as little downtime for the
site as possible.

My idea was to use a subdomain of staging, perform all the neccesary 
migrations and tests, then flip flop the www domain with the staging
and update the WordPress database URLs. Not a bad idea, and would
give minimal downtime for sure. 

The main problem was that the old system is a single server instance on
media temple, while the new system was going to be one on Amazon, with
an s3 bucket, RDS, and cloudfront cdn services. So there didn't seem to
really be a way to 'test' the full system except by going live with it.

After some reflection one of my coWorkers had a brilliant idea. There's
no need to update the DNS just to test the whole thing at all! Browsers
can be tricked! So, it was as simple as pinging the load balancers public
address, grabbing the ip from a ping. And then adding entries into the 
hosts file on our and the load-balancer systems to point the site's url
to the ip of the load balancer. 

So, what did that accomplish? Well, since the computer will check the 
hosts file first, the browser looks up the site's url, sees the host file
first, and runs off to the ip address instead of asking a name server
out on the internet for the address. By adding the CDN subdomains to the
hosts file as well, the entire system can be tested, without actually
switching hosts over! AND as an added bonus, the production site will
continue to exist in maintenance mode for all to see like no giant awesome
change is happening at all, until it's revealed!

That's some damn good trickery.