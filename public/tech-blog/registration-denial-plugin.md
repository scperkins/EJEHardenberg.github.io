### Simple Email Filter and Banning Plugin for WordPress

In my [last post] I showed you how to make a really simple, programmatically 
maintained filter to deny registration on your WordPress sites. But, if you're 
the average user, you probably don't want to dive into source code when you're 
updating a list of spam mails, especially since they might change often or you
just like a graphical interface for your administrative work. 

Either way, [I've got you covered] with my new plugin. I'm calling it ** Simple 
Email Filter & User Ban **, a lengthy, but correct name.

Here's how it works, first up you install and activate the plugin like you do 
any other WordPress plugin. Then you'll notice a couple of new things.

#### In the **Users** listing you'll have a new column and new actions

You'll be able to see the last known IP Address of a user who has logged into 
your site. This is useful for using [iptables] to drop packets from malicious 
users who don't know how to evade those types of things.

<img src="/images/tech-blog/sef/ipaddr.png" width="700px"/>

You'll also notice that when you hover over a user you'll be able to click an 
action button to ban or unban that user.

<img src="/images/tech-blog/sef/unban.png" />
<img src="/images/tech-blog/sef/ban.png" />

Once banned, whenever they try to log in they'll get a nice message that you can 
set in your **wp-config** file like this:

	define('SEF_BAN_MESSAGE', 'It seem\'s you\'ve messed up and are banned, contact the site owner');

And it will look something like this on their site:

<img src="/images/tech-blog/sef/banned.jpg" />

#### A new options page is available for you!

In the Registration Denial's setting page, you'll be able to manage the list of 
domain and strings that you won't accept registrations from. This means no more 
managing the programmatic list and using a simple list interface instead

<img src="/images/tech-blog/sef/settings.png" />

Once you've listed the domains you count as spam, you'll be able to live in 
moderate peace while the spam users will only see messages like this:

<img src="/images/tech-blog/sef/denied.png" />

As with the ban message, you can set the denial message from **wp-config** as well:

    define('SEF_DENY_MESSAGE', 'Registration halted, please contact support.');

#### And that's it!

Enjoy! If you have ideas or enhancements feel free to send me a pull request on 
[github], and if you have any problems you can open an issue there. The source 
code is Open and freely available for modification, though I of course appreciate 
a backlink and a mention if you use my code.


[last post]:registration-denial-wordpress
[I've got you covered]:https://github.com/EdgeCaseBerg/simple-email-filter
[iptables]:http://www.cyberciti.biz/faq/linux-howto-check-ip-blocked-against-iptables/
[github]:https://github.com/EdgeCaseBerg/simple-email-filter