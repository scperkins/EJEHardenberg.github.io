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

Another MIME type to be wary of in emails is the `multipart/*` set. The 
content in the subtype has some important rules, most notably [RFC 1521]
states:

>Systems should recognize that the content of the various parts are interchangeable. Systems should choose the "best" type based on the local environment and preferences, in some cases even through user interaction. As with multipart/mixed, the order of body parts is significant. In this case, the alternatives appear in an order of increasing faithfulness to the original content. In general, the best choice is the LAST part of a type supported by the recipient system's local environment.

Which means that during parsing one should take the order into account 
along with what view the user will see. Sending HTML back to a plain 
text viewer wouldn't make any sense now would it? And displaying 
unformated text to a user of a rich UI would be missing an opportunity.

Let's just focus on how to read from the [MIMEMessage] type first, the 
message can have many different parts, so it's important to determine 
what you're dealing with. The `getContentType` method might be your 
first choice because of the name, however then you'll be parsing the 
header yourself. A more useful indication is `isMimeType` which enables
one to check the primary (like text) and sub (plain, html) type of the content. Once you do this, you can determine which type to cast the 
result of the `getContent` method to. If you're interested in just 
text for example, you can use the wildcard \* for the subtype:

	def getTextFromBodyPart(p: javax.mail.Part): Option[String] = {
		if (p.isMimeType("text/*")) {
			Some(p.getContent().asInstanceOf[String])
		} else {
			None
		}
	}

If you wanted to get something more complicated, like a multipart 
message, you'd check `isMimeType("multipart/*")` then use `asInstanceOf` 
with [MultiPart]. The trick with handling the [Multipart] class is that 
you need to handle the _multiple parts_ (obvious, yes, but still tricky).
Here is a "simple" case of parsing a mimeMessage that _mostly_ works:

	case class SimpleEmail(to: List[String], from: List[String], subject: String, plain: Option[String], html: Option[String])


	def mimeMessageToSimpleEmail(mimeMsg: MimeMessage): SimpleEmail = {
		val subject = mimeMsg.getSubject()
		val senders = mimeMsg.getReplyTo().toList.map(_.toString())
		val recipients = mimeMsg.getAllRecipients().toList.map(_.toString())
		/* Now the annoying part. The Message itself and all the disposition and such */
		val mailParts = mimeMsg.getContent().asInstanceOf[Multipart]
		var plainText = Option[String](null)
		var htmlText = Option[String](null)
		for (p <- 0 until mailParts.getCount()) {
			val bodyPart = mailParts.getBodyPart(p)
			if (bodyPart.isMimeType("text/*")) {
				if (bodyPart.isMimeType("text/html")) {
					htmlText = getTextFromBodyPart(bodyPart)
				} else {
					plainText = getTextFromBodyPart(bodyPart)
				}
			} else if (bodyPart.isMimeType("multipart/*")) {
				val multiPart = bodyPart.getContent().asInstanceOf[Multipart]
				for (mp <- 0 until multiPart.getCount()) {
					val part = multiPart.getBodyPart(mp)
					if (part.isMimeType("text/plain")) {
						plainText = getTextFromBodyPart(part)
					} else if (part.isMimeType("text/html")) {
						htmlText = getTextFromBodyPart(part)
					}
				}
			}
		}

		SimpleEmail(recipients, senders, subject, plainText, htmlText)
	}

The above code is an adaptation on some I found on [coderanch] that 
provided some insight. Unfortunately, this code has a flaw.


[GreenMail]:https://github.com/greenmail-mail-test/greenmail
[great blog post on using it with JUnit]:http://developer.vz.net/2011/11/08/unit-testing-java-mail-code/
[Play Mailer Plugin]:https://github.com/playframework/play-mailer
[MimeMessage]:https://javamail.java.net/nonav/docs/api/javax/mail/internet/MimeMessage.html
[RFC 1036]:https://www.ietf.org/rfc/rfc1036.txt
[RFC 1521]:http://www.freesoft.org/CIE/RFC/1521/18.htm
[MultiPart]:https://javamail.java.net/nonav/docs/api/javax/mail/Multipart.html
[coderanch]:http://www.coderanch.com/t/597373/java/java/Body-text-javamail-retrieve-email