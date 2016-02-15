### Elastic Search Java API Examples

#### Motivation

I've been enjoying elastic search recently and looked at a few different 
wrappers in Scala. There's [elastic4s], [jest], and [spring's]. But I 
think that learning fundamentals is important, elastic4s provides a DSL 
around the Java API, but if I want to really understand it, then I need 
to use it directly. 

Unfortunately, there's not too much in the way of tutorials online. I 
found a few, but a lot of the time while working I was running to the 
JavaDoc for reference. I don't know about you, but I work through 
examples better than I do at reading reference material and picking 
apart how various classes are supposed to work with each other. The most 
important thing is to _use the right version_ of the JavaDoc or you're 
going to be hopelessly confused. You can find [JavaDocs for each version of elastic search here].
And for this blog post I'll be using 2.2.0 (The current head) but you 
should be able to use _most_ of the code I believe, and if not, comment 
and ask for an example if you need one and can't figure it out.

#### Quick Note

All of these examples are available on my github, so if you're impatient 
and want to just grab the code and run it yourself, [here's the link].

#### Setup Elastic Search

The repository contains 


[elastic4s]:https://github.com/sksamuel/elastic4s
[jest]:https://github.com/searchbox-io/Jest
[spring's]:https://github.com/spring-projects/spring-data-elasticsearch
[JavaDocs for each version of elastic search here]:http://javadoc.kyubu.de/elasticsearch
[here's the link]:https://github.com/EdgeCaseBerg/elasticsearch-examples