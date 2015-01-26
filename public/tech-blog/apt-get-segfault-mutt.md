### Apt-get not working to install mutt, segfault!

I was thinking I'd try fiddling around with mutt and seeing if I liked it or not
today. Of course, it's difficult to do that when your package manager suddenly 
stops working. While attempting to run `apt-get install mutt` the messages showed
the usual reading messages, but then suddenly exited with no error message. 

Thinking this was strange I checked the output of `dmesg`

	[ 4847.938200] apt-get[4338]: segfault at 7fa34e62c0a8 ip 00007fa318fc92d3 sp 00007fff6a66b970 error 4 in libapt-pkg.so.4.12.0[7fa318f74000+121000]
	[ 4862.992835] apt-get[4349]: segfault at 7fd57d8cb0a8 ip 00007fd5482682d3 sp 00007fffbffd9950 error 4 in libapt-pkg.so.4.12.0[7fd548213000+121000]
	[ 4876.220520] apt-get[4365]: segfault at 7f327a19e0a8 ip 00007f3244b3b2d3 sp 00007ffff5e5f0e0 error 4 in libapt-pkg.so.4.12.0[7f3244ae6000+121000]
	[ 4987.237685] apt-get[4395]: segfault at 7f14a04570a8 ip 00007f146adf42d3 sp 00007fffb319dde0 error 4 in libapt-pkg.so.4.12.0[7f146ad9f000+121000]
	[ 5301.692825] apt-get[4667]: segfault at 7feedf5270a8 ip 00007feea9ec42d3 sp 00007fff5d0c3980 error 4 in libapt-pkg.so.4.12.0[7feea9e6f000+121000]
	[ 5306.932056] apt-get[4673]: segfault at 7f61488a20a8 ip 00007f611323f2d3 sp 00007fffbff58210 error 4 in libapt-pkg.so.4.12.0[7f61131ea000+121000]
	[ 5355.102636] apt-get[4682]: segfault at 7fbf997fd0a8 ip 00007fbf6419a2d3 sp 00007fff24de0dd0 error 4 in libapt-pkg.so.4.12.0[7fbf64145000+121000]
	[ 5417.063910] apt-get[4751]: segfault at 7f875b7c90a8 ip 00007f87261662d3 sp 00007fffca9d44e0 error 4 in libapt-pkg.so.4.12.0[7f8726111000+121000]

Well that doesn't seem good! Segfaults are never good to see in your message log.
So I searched [online] and found a forum that seemed to have the issue. After 
seeing a post mention cleaning their apt-get cache I checked the man page and 
tried out a quick `apt-get clean` and then I was able to install again! 

Hope this helps someone out there!


[online]:http://ubuntuforums.org/showthread.php?t=2209984
