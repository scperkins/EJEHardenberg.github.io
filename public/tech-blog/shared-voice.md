### Shared Voice 

Yesterday I was thinking to myself about how useful [Twitter] can be for 
[internet](https://archive.today/bLdK0) [activism](http://en.wikibooks.org/wiki/Professionalism/Hacktivism) and [protests](http://www.millionmaskmarch.com) and trying to figure out how I could lend my talents 
to activists everywhere. 

I've known about [thunderclap] for a while, but one of the things I see as a flaw
is that it doesn't really jive well with anonymous culture. For example, consider 
the case study here:

You're an activist who has found something troubling, you've decided to be a 
whistleblower, but you need to get your message out to as many people as possible. 
Organizing a Thunderclap is public, which means that you're going to lose some of
the shock element from your leak.

So what do you do? 

<img src="/images/tech-blog/shared-voice.png" width="800px"> 

Well, I've made [SharedVoice], which is an extremely simple twitter application 
that solves this usecase. It's simple and developer friendly: setup a simple 
webserver with Apache, MySQL, and PHP by following the [setup instructions] and
then setup your configuration file named *conf.json*, something like this:

	{
		"apiKey" : "YourTwitterAPIKey",
		"apiSecretKey" : "YourTwitterAPISecretKey",
		"dbname" : "databasename",
		"dbuser" : "databaseuser",
		"dbpass" : "databasepass",
		"dbhost" : "databasehost",
		"tweet" : "Anonymous exposes cop as member of KKK behind letter threatening to kill #Ferguson protesters http://bit.ly/11c5xIq	"
	}

Once this is setup, the text in the "tweet" will appear on the page. In the screenshot
above, the text there was "This is a test. Pay no mind. This is a test". After 
you've got the small page setup, you can simply start sharing the link to people 
you trust to spread your sentiments, and then once you're ready, hop onto the 
server to run `post.php` or setup a cronjob to fire at a specific time/date.

It's a simple tool, but I'm hopeful that someone will make use of it. As far as 
version's go, you'll need to use PHP < 5.5 since the `mysql_*` functions are 
deprecated after that point. 

[Twitter]:http://twitter.com
[thunderclap]:http://thunderclap.it
[SharedVoice]:https://github.com/EdgeCaseBerg/SharedVoice
[setup instructions]:https://github.com/EdgeCaseBerg/SharedVoice/blob/master/setup.md