### Request Bodies and Java

There's RFCs and there's the real world. Unfortunately, these two don't 
always play together. [RFC 2616] defines HTTP methods and their rules 
and then there's an the implementation in Java's HttpURLConnection. 

RFC 2616 states 

>The presence of a message-body in a request is signaled by the
>inclusion of a Content-Length or Transfer-Encoding header field in
>the request's message-headers. A message-body MUST NOT be included in
>a request if the specification of the request method (section 5.1.1)
>does not allow sending an entity-body in requests. A server SHOULD
>read and forward a message-body on any request; if the request method
>does not include defined semantics for an entity-body, then the
>message-body SHOULD be ignored when handling the request.

In plain english, this means that if you're sending a request body then 
servers should _always_ forward it, even if they don't use it, unless 
the specification for that method type forbids bodies explicitly (Like 
the TRACE method). So when you're working with ElasticSearch or with a 
custom application that expects a request body in say, a GET or a DELETE 
request, you'd expect the body to make it to the server. 

	java.net.ProtocolException: HTTP method DELETE doesn't support output at sun.net.www.protocol.http.HttpURLConnection.getOutputStream(HttpURLConnection.java:1082)

Oops, because of a [bug], you can't do this in java versions less than 
1.7 for _non-https_ connections. 

The reason for this is the code around the `getOutputStream` method 
within the [HttpURLConnection] class:

	if (method.equals("GET")) {
	   method = "POST"; // Backward compatibility
	}
	if (!"POST".equals(method) && !"PUT".equals(method) &&
	   "http".equals(url.getProtocol())) {
	   throw new ProtocolException("HTTP method " + method +
	                               " doesn't support output");
	}

_Why_ and _when_ only POST and PUT were allowed to have output is 
beyond me (I don't want to try to read [the file log] without a blame 
tool to inspect those lines). But it _is_ fixed [in Java 8]. But the 
fix has not been backported to java 6 or 7 unfortunately. 

Perhaps the oddest thing is that the "work around" for needing to send 
a body with a DELETE request. The work around is to use HTTPS rather 
than HTTP. I've scanned the latest RFC, [RFC 7230 Section 3.3], and 
haven't found any indication of _why_ the `http.equals(url.getProtocol())` 
line exists (But if you know, please comment and tell me where to read).
Luckily, because [Let's Encrypt] exists, you can get a certificate to 
have a valid HTTPS connection without having to shell out hundreds of 
dollars for it. Regardless, it would still be nice if the fix was backported 
to Java 6 & 7. 


[bug]:http://bugs.java.com/view_bug.do?bug_id=7157360
[RFC 2616]:https://www.ietf.org/rfc/rfc2616.txt
[HttpURLConnection]:http://grepcode.com/file/repository.grepcode.com/java/root/jdk/openjdk/7u40-b43/sun/net/www/protocol/http/HttpURLConnection.java#1076
[the file log]:http://hg.openjdk.java.net/jdk7/jdk7/jdk/log/9b8c96f96a0f/src/share/classes/sun/net/www/protocol/http/HttpURLConnection.java
[in Java 8]:http://hg.openjdk.java.net/jdk8/jdk8/jdk/rev/fd050ba1cf72
[RFC 7230 Section 3.3]:https://tools.ietf.org/html/rfc7230#section-3.3
[Let's Encrypt]:https://letsencrypt.org/
