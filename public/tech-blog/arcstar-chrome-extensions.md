### A First Foray into Chome Extensions

Yesterday I created [\*arc] a simple productivity tool for chome. It lets people archive websites a little bit easier. My main use case is
just saving information that someone might choose to delete later. 

- Politicians who need to be held accountable for things they say online
- Public figures who need to be held accountable
- Threats made against someone 
- Evidence of harassment or bullying online

A [recent website] let's you easily save tweets, they've got a 
bookmarklet and an API as well. So I thought to myself, it'd be nice to 
be able to save a tweet with a single click, and if you're on a website 
be able to save that as well. While thinking about this, I decided it'd 
be better to have a single button and have it be context aware of the 
current tab open.

This led to some pretty simple code:

	var arcGenerator = {
	  genArc: function(url) {
	    /* If on twitter also send to tweetsave */
	    if(url.match(/twitter.com/)){
	      setTimeout(function(){
	        open('http://tweetsave.com/?tweet='+encodeURIComponent(url))
	      },10)
	      
	    } 
	    setTimeout(function(){
	      open('https://archive.today/?run=1&url='+encodeURIComponent(url))  
	    },10)    
	  },
	};

	document.addEventListener('DOMContentLoaded', function () {
	  chrome.tabs.query(
	    {
	      'active': true,   
	      'windowId' : chrome.windows.WINDOW_ID_CURRENT
	    }, 
	    function(tabs){
	      var tab = tabs[0];
	      var url = tab.url;
	      arcGenerator.genArc(url);
	    });
	});

And that's it, there's the _manifest.json_ file as well, and a popup.html to call the code above, which you can find in the [repository]. 
The only issue I ran into was getting the current tab from the extension.

The code above will work with the latest chromium and chrome, In chromium
you can use either:

    chrome.tabs.query({'active' : true, 'windowId' : chrome.windows.WINDOW_ID_CURRENT})

or

    chrome.tabs.query({active: true, lastFocusedWindow: true})

But the latest stable build of chrome (38.0.2125.111) will give you a bad
result from the second. The only caveat I can say to that is that when 
the second option wasn't working, I didn't have the `"tabs"` permission 
in my manifest file. So it may just have been that issue and both work.

Either way, the extension is out there, and literally took less than a
half hour to make. The only thing I'd call tricky about it would be that
in order to have both TweetSave and Archive.today open from a single click, it is neccesary to use the `setTimeout` function to wrap both the
`open` calls.

If you find the extension useful let me know! I'd be interested in 
hearing what it's being used for and if it's helping anyone.

The Google Chrome Store was easy to use, pay $5.00 for your developers 
access to the store (the terms say it's to help weed out spam). Then the
developer dashboard is easy to navigate and update your plugins. The only
suggestion I'd make to Google would be to make a "Your Apps" link to your
own developed apps from the main chrome store page, instead of having to 
go to the developer center first, then see the link. It'd be nice to have
a faster way to share the url of your own plugins.

[\*arc]:https://chrome.google.com/webstore/detail/arc-one-click-archiving/hmbmdbfkpgemaefgbinhcfodneaocfeg
[recent website]:http://tweetsave.com/
[repository]:https://github.com/EJEHardenberg/arcsave