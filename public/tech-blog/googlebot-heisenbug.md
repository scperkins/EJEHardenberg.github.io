###The Invisible Hand of Google

Today I ran into one of the more interesting bugs I've seen recently. The problem
started occuring when a work client's site started seeming to misbehave. Namely,
their voucher system was redeeming themselves it seemed. 

So we started looking at it and noticed that the redemptions were occuring pretty 
soon after they were purchased. Setting up a test deal, we started recreating the
problem on the live site (I tried futilely to trace the steps and perform the same
sequence on my local environment to no avail.), with this success (recreating the 
problem is the first step in debugging) I began inserting logging around the area
of the database that handled the updates.

Soon enough we saw the tell-tale logs come through, but they didn't make any sense.
Our tester had taken no action, and hadn't done anything that would have caused
any response from the page. So, I took the next logical step: something automated was 
going on.

I checked the cron logs for anything suspicious, then moved to triggering the jobs
themselves to look for anything strange. Finally, I threw the sledge hammer at it
and threw in this gem:

    hs_log("FROM UPDATE: $id " .('server::' . print_r($_SERVER,1)) . ('GETS::' . print_r($_GET,1)) . ('POST::' . print_r($_POST,1)), 1 );

And had our tester run through the bug producing sequence one more time. Then I 
waited for the large amount of arrays to fly by my screen. Stopped it, snagged it,
and copy pasted it to my text editor for inspection.

I burst out laughing when I saw it -- ` [HTTP_FROM] => googlebot(at)googlebot.com\n `
The problem was from a spider! Here's what had happened: One of the ways redemption
is done on this client's site is through QR codes. When the QR code is followed, 
the voucher is instantly redeemed. It's an easy process for the person having
their voucher redeemed and is speedy overall, the problem is that just by following
the link that the QR code represents the voucher is marked redeemed.

So what had been happening was that google had looked the page for the voucher,
then saw the link for the QR code, and innocently followed that link trying to
index the website. The fix of course was simple:

	if(isset($_SERVER['HTTP_FROM'])){
		if(strpos($_SERVER['HTTP_FROM'], 'google') !== false){
			hs_log("PROTECTED FROM GOOGLE SPIDERS",1);
			return;
		}
	}

Within the code that decides to redeem the voucher form the QR code or not. It 
was an interesting bug to find, and thankfully an easy one to fix. The php check
is there as a safeguard and a robots.txt will follow to tell the spiders to lay 
off.