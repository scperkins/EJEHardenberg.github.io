### Creating your own RSS feed with HarpJS

A lot of people use RSS feeds to aggregate content they want to know 
about, and by offering this service from your own website or blog you 
can help distribute your content a little bit easier to the tech-savvy 
world. The other day one of my friends asked me if **my** website had an 
RSS feed. 

It does now. And I'm going to show you how to do get your own.

As you know if you've read my [previous posts] I use [HarpJS] to compile 
my website whenever I create new content. Harp let's you use EJS or Jade 
to template your website and supports a lot of different content types 
out of the box. Specifically, I write everything in [markdown] because I 
love it, and luckily for you and your RSS feed, Harp supports creating 
XML documents as well, including templating.




[previous posts]:harp-and-smut.html
[HarpJS]:http://harpjs.com
[markdown]:daringfireball.net/projects/markdown/syntax