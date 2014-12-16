### GoToDocumentation Sublime Text 2 and Chromium

Today I installed the [Goto Documentation] package for [Sublime Text 2],
I don't normally use a lot of packages, but I came across a blogpost about 
some interesting ones, and this figured I'd try one out.

The package is simple, you press: `SUPER+CTRL+H` while your cursor is on 
a native function, and you'll get the documentation for it opened in your 
web browser. For PHP this opens [php.net], for C++ it opens [cplusplus.com], 
and I haven't tested it with anything else yet. The issue I ran into, which 
seems to be common on Linux Mint, is that the default web browser refuses 
to change over to chromium.

In fact, on inspection of the source code of the webbrowser python module,
there's 0 mention of chrome at all. After some internet sleuthing I happened 
on [this stackoverflow post], and after realizing that my system has Python 
2.7 and not 2.6 (and no amount of tabbing with `/usr/lib/py` would change that)
I opened up the `webbrowser.py` file and updated it to look like this:


	58 def open(url, new=0, autoraise=True):
	59     for name in _tryorder:
	60         browser = get('/usr/bin/chromium %s')
	61         if browser.open(url, new, autoraise):
	62             return True
	63     return False
	64 
	65 def open_new(url):
	66     return open(url, 1)
	67 
	68 def open_new_tab(url):
	69     return open(url, 2)

A quick and dirty hack, and definitely not ideal (I should take out the `for` loop)
but _after_ restarting sublime, I was pleased to discover that the hotkey now 
opened my documentation in my browser of choice. I then proceeded to close the 
[issue] I had opened about it on the Goto Documention package's github.

Isn't Linux grand? Hope this helps someone else hack their sublime installation.


[this stackoverflow post]:http://stackoverflow.com/questions/6042335/calling-chrome-web-browser-from-the-webbrowser-get-in-python
[cplusplus.com]:http://www.cplusplus.com/
[php.net]:http://php.net/manual/en/index.php
[Sublime Text 2]:http://www.sublimetext.com/2
[Goto Documentation]:https://github.com/kemayo/sublime-text-2-goto-documentation
[issue]:https://github.com/kemayo/sublime-text-2-goto-documentation/issues/43