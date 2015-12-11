### How to test the PlayFramework Mailer

At some point in your life, you're going to have to deal with Email. A 
seemingly simple thing, after all, it's just a subject, body and some 
addresses right? Well, there's way more to it than that. But perhaps the 
most troublesome about it is that it's hard to test.

Or at least normally, setting up a local SMTP server just to test that 
your code works is a pain. Trying to integrate a local SMTP setup into 
a build server or any kind of project shared between someone other than 
you? Worse! So what can you do? Well, say hello to [GreenMail]. 

>GreenMail is an open source, intuitive and easy-to-use test suite of email servers for testing purposes. Supports SMTP, POP3, IMAP with SSL socket support. GreenMail also provides a JBoss GreenMail Service. GreenMail is the first and only library that offers a test framework for both receiving and retrieving emails from Java.

In other words. It's your testing dream. There's already a [great blog 
post on using it with JUnit], but what if you're using scala? What if 
you're using the [Play Mailer Plugin]? Well thats just fine, since it's 
all SMTP or POP anyway. Though there are some things to keep in mind:

1. Set `smtp.ssl` in your **test** configuration to `false`
2. Make sure to set `smtp.port` to the same as GreenMail
3. Java's [MimeMessage] is a pain to parse 

The first two of these are easily addressed when you create a test: 

	import org.scalatest._
	import play.api.test.Helpers._
	import play.api.test._
	import com.icegreen.greenmail.util.{ GreenMail, ServerSetup }
	...
	val mailPort = 30003
	val greenMail = new GreenMail(new ServerSetup(mailPort, null, "smtp"));

	"Some test" should "use the right config" in running(		
		FakeApplication(
			additionalConfiguration = Map(
				"smtp.host" -> "localhost",
				"smtp.port" -> mailPort,
				"smtp.ssl" -> false
			)
		)
	) { ... }


<small>
**Tip:** You can make this a lot more readable by putting the 
`FakeApplication` creation into a helper function and calling that.
</small>

The second is more troublesome. While you might think that the text of 
an email is just that, you'd be wrong. An email, at least in MIME style,
can have multiple parts. Each of which might have different MIME types 
and dispositions. MIME types are your normal things like `text/html`, 
`text/plain`, and etc. Disposition defines whether or not the content 
of the message should be shown to the user as an attachment or inline 
with the body of the email. 

Another MIME type to be wary of in emails is the `multipart/*` set.




[GreenMail]:https://github.com/greenmail-mail-test/greenmail
[great blog post on using it with JUnit]:http://developer.vz.net/2011/11/08/unit-testing-java-mail-code/
[Play Mailer Plugin]:https://github.com/playframework/play-mailer
[MimeMessage]:https://javamail.java.net/nonav/docs/api/javax/mail/internet/MimeMessage.html