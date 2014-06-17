One of the projects at my workplace has got me diving into WordPress. Should be
easy right? It's php, one of the simplest, easy to use (besides it's dreadful
$ symbol before everything), and dynamically typed languages out there. What 
could go wrong?

Simple: Everything. If you want to do custom code in a WordPress site, you make
a plugin. Sounds easy enough, sounds like Drupal's modules. Cool. That makes 
perfect sense to me. But then came the learning curve. 

Luckily the [Codex] has a ton of information, and there are some great tutorials
out there. But anything involving how to run just a standard php file was near
impossible to find. All I wanted to do was be able to say: This URL goes to This
file, without making an .htaccess file. And it seemed impossible. 

Luckily, I had an example (sort of) of how to make a custom router.
Granted it was nested heavily into a massive plugin that I had to search
through. But it used the technique of making objects that were
associated with custom post types in order to serve it's content. 

Well that was great. But I only really wanted to serve a single page.
Not a bunch of posts. I could programatically create a page from my
plug-in and then try to somehow hook up listening to JUST that page with
a slug of some kind and then make the template include my file? 

But that seemed messy. There had to be a clean way. So I got thinking.
Well, if they can include custom post types, then I can make just one
and then keep a reference to it some how. Simple enough. Use get_option
to check the ID of the post I'll make from some initializing function. 

So I did that (after some trial and error where I forgot to hook into
the init hook of wordpress before calling wp_insert_post -- which fails
by the way, fatally. No WP_Error or anything) and bam. It was working. 

The best part of the whole routing system was that since I was capturing
my php files output in the output buffer (ob_start and friends). That
content was then sent to wordpress as a string to be interpreted as the 
content of the post being rendered onto the page. This means that any 
shortcodes in the php files output were expanded. 

This is actually very cool because it allows me to integrate the 
flexibility of my php code with the simplicity of shortcodes. Essentially
I ended up with my own meta language to write my views in. A nice combination
of php and shortcodes. 

I made a small plugin called [qroute] that does this routing. And tested 
the shortcode output with a few custome [shortcodes]. If you need nesting
of shortcodes (which is likely), you just need to call do_shortcode on 
whatever the string being returned from the other shortcodes is. 


[shortcodes]:https://github.com/EJEHardenberg/dealcodes
[qroute]:https://github.com/EJEHardenberg/qroute
[Codex]:codex.wordpress.org
