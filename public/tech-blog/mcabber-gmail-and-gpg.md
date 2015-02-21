### Mcabber and PGP 

Today I decided to play with a number of new things. One was conky: 

<img src="/images/tech-blog/conky.png" />

And the other was [mcabber]. A simple chat client that uses the [jabber
protocol]. Those of you who are used to using Facebook Chat, GChat, and
other website specific chat application might wonder why you'd ever want
to use a desktop application. After all, most of us stopped using [AIM]
in the late 2000's. 

But back in those simple times we were all used to having our own chat
clients instead of storing everything in 3rd party servers. Not to say
everything wasn't logged then as well, but you know, ahem. Anyway! This
is how to connect to the google chat servers via mcabber and then use
pgp to encrypt your communications.

Using your favorite package manager download mcabber and gpg. The best
guide for setting up and understanding gpg can be [found here] if you
need to set that up. Once you've got mcabber downloaded you'll need to
create your configuration file: **~/.mcabberrc**. 

	set jid = <your gmail address>
	set username = <your gmail address>
	set server = talk.google.com
	set port = 5223
	set priority = 4
	set ignore_self_presence = 1
	set ssl = 1
	set ssl_verify = 1
	set logging = 0
	set pgp =1 
	set pgp_private_key = <use gpg --fingerprint --list-secret-keys>
	set beep_on_message = 1
	
You can find more configuration options online with google or looking
through documentation. One that I found which had a lot of good comments
can be read [here]. As noted above, you'll want to put your own email
address for the `jid` and the `username`. Then use the long form of your
private key from `gpg --fingerprint --list-secret-keys`. 

Once this is done you're pretty much there but getting used to mcabber
can be improved by mastering a few simple commands. 

- Use the pgUp and pgDown keys to select a buddy in the roster list on
  the left, the type enter to open a chat with them. 
- `/roster unread_first`: This command will bring your chat window
  instantly to any unread messages. A must for talking to multiple
  people.
- `/roster hide_offline`: This command removes offline people from your
  chat roster.
- `/roster search <name>`: will let you quickly jump to a contact in the
  roster so you can chat with them. (much faster than pgDown)
- `/roster alternate`: Switches between the current and last used chat
  session.
- `/pgp setkey <email> <longid>` sets the pgp key to use when talking to
  the user who's email address is <email>. 
- `/quit` how to close mcabber! 

mcabber does have tab complete, so you can quickly do these commands
that way, it also supports bindings. For example, within your mcabberrc
file you can do things like this: 

	bind 17 = quit #q for quit
	bind 24 = roster unread_first #x for jumping to next message
	bind 26 = roster toggle_offline #z for toggling offline people 
	alias me = say /me 

When experimenting with the pgp encypted chatting, it's a good idea to
use the `/info` and `/pgp info` commands to determine if you have
another user's keys or not and to verify that the key is the same one
you have stored in your gpg chain (use `gpg --list-keys` to check). Once
you've confirmed that you're using the right keys, [according to the
manual] if you have `set pgp = 1 ` within your rc file then your
communications will automatically be encrypted. However, when testing
this with a friend of mine we noticed this wasn't always the case and on
occasions we needed to use `/pgp info` before the encrypted
communications would begin, or we needed to use the `pgp setkey
foo@bar.net KEYFROMPGPKEY` command to set the key ourselves. 
	
Him and I troubleshot the problem for a bit, eventually giving up around
1am in the morning after being unable to figure out why my client would
automatically encrypt messages but his required a `/pgp force` command.
If you run into similar issues here are a few things to check: 

- `/pgp force` will show you errors in the log box if there's something
  wrong, read them, they'll help troubleshoot
- `gpg --list-keys` and make sure you've got their key and that the id
  matches the one from `/pgp info <email>`
- If you have multiple keys for the same email (such as if you use
  keys,gnupg.net and pgp.mit.edu for keyservers) make sure you have the
  most updated keys from both then check the above step again
- if you see the `-~>` that means the message was sent encrypted. If
  it doesn't have a `~` then it's not encrypted! 
- `/pgp enable` and `/pgp setkey`are your friends! 

All said and done, you might ask yourself, _why_? Why should you
encrypted your chat conversations? Well there's plenty of reasons. For
example, what if you're talking about something like a disease? A close
family death? Or anything like that that you don't think anyone else
should know? What if you're an activists staging a protest and you
want to be sure that it comes as a surprise for maximum impact (and
you're wearing your tinfoil hat)? What if you're a journalist chatting
with a leak source? What if you're a leak chatting to a journalist? Or a
developer talking to another and exchanging passwords for a database or
web server? There are plenty of reasons to want to encrypt your chat 
that aren't nefarious. And mcabber and gpg make it very simple to have 
automatic encryption right away. 


[mcabber]:http://mcabber.com
[jabber protocol]:http://www.jabber.org/
[AIM]:https://www.aim.com/
[found here]:http://digitalocean.com/community/tutorials/how-to-use-gpg-to-encrypt-and-sign-messages-on-an-ubuntu-12-04-vps
[here]:http://pastebin.com/wP9PJLq9
[according to the manual]:http://mcabber.com/files/mcabber_guide.pdf
