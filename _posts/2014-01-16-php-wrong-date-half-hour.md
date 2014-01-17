---
title: Incorrect Time in PHP despite Timezone
layout: post
---

Today I was configuring a server's system time, the server was an Amazon
one and after setting the php.ini file's `date.timezone` field I found a
perplexing output from running php's date functions.

The time was off by a half hour! 

This was quite odd since it wasn't a whole hour. After thinking a bit and
checking the php.ini settings, I looked at the date.default_latitude and 
date.default_longitude fields. They were set to somewhere in turkey. 
Editing these two fields to point to within the same timezone as the one
I had set caused the time to switch to the correct one.

Very strange! According to the php documentation, those configuration 
settings only effect the sunrise functions. Apparently not!