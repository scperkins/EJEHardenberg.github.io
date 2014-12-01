###Private Talk. A simple chat server behind apache

I've been [into CGI recently] and wanted to continue the trend. So I
started a [new project] to make a small chat server. You might ask
yourself, why do that? Everyone uses facebook Chat or G+ chat
now-a-days. No one uses AIM or Yahoo to message people anymore. 

And to that I say: yeah but **everyone** stores your data.<sup>*</sup>

So recent life events have left in me in a situation where one of my
closest friends is going to be overseas for a while and I wanted a way
to talk to them. Following the opposing view to the [NIH] principle and
satisfying my natural curiousity of how hard it would be to make a chat
server, combined with this situation has resulted in a small chat server
being made.

It was really easy. 

So easy in fact, that I'm thinking I will write a couple blog posts with
tutorials in them on how to make your own private chat server. I think
it will be fun, and hopefully helpful to people learning everywhere. The
structure of the tutorial will probably be something like this: 

 - Introduction to qdecoder and apache CGI
 - Creating a register and login system with qdecoder
 - Creating a chat program with C and apache

I'm hoping that will be an alright pace for things and will probably
provide sample code as some type of small library. 


<sup>* Not everyone, for example there is this [excellent project] going
on:  </sup>

[excellent project]:http://labs.bittorrent.com/experiments/bittorrent-chat.html
[into CGI recently]:http://www.ethanjoachimeldridge.info/tech-blog/bgi
[new project]:https://github.com/EdgeCaseBerg/pChat
[NIH]:http://en.wikipedia.org/wiki/Not_invented_here
