### MySQL DATE type and JDBC connection conversion issues

Today I was working on my side project [accountable] and ran into the fun
of trying to line up timezones between the application and the MySQL 
server I'm using. I say fun because this of course involves the infamous 
[java.util.Date], which has been a [pain to developers] [for ages]. 

In my application, I create [Instant] classes since that's the recommended 
way to go now. And for my purposes I wanted to store them as UTC that way
I can convert them to any locale I'd like to later on, since I'm also 
only concerned about the date and no hours, I used the [MySQL Date type] 
for my database table, this, when combined with [Anorm's parser] leads me 
to the use of the `Date` class in my code.

The [failing test] was failing with an odd error. When creating and 
persisting my domain class to the database, the `dateOccured` field
would read as the correct UTC timestamp. However, when reading the 
field back out of the database when retrieving that same instance, I'd 
see a change equal to my timezone. This struck me as a bit odd, since I
had spent some time trying to make sure I created UTC and stored UTC 
dates.

After a few hours scratching my head I came to the conclusion that I must
have done something wrong, and when I found my pre-database-insertion 
code using my system zone I thought to myself, ah of course! 

	val localTime = ZonedDateTime.ofInstant(Instant.ofEpochSecond(expense.dateOccured), ZoneId.systemDefault)

Clearly, this must be it. After all, that's where the extra hours might 
come from right? And changed it promptly to:

	val localTime = ZonedDateTime.ofInstant(Instant.ofEpochSecond(expense.dateOccured), ZoneId.of("UTC"))

But unfortunately, this wasn't the case. It simply _shifted_ my hours for
both the stored instance _and_ the returned instance. Remembering that 
the [MySQL Date type] documentation mentions some conversions on storage, 
I figure'd I'd read it again:

>MySQL converts TIMESTAMP values from the current time zone to UTC for storage, and back from UTC to the current time zone for retrieval. **(This does not occur for other types such as DATETIME.)**

So it's _only_ for the TIMESTAMP type, not for the type I'm using here. 
This meant that it had to have _something_ to do with the java client 
itself. Looking at the [connector paramaters one can pass to the JDBC] 
it became clear that the client was performing a conversion from the 
client side of the connection to whatever the server was speaking in. 
Checking the timezone of the server is fairly simple from a MySQL CLI:

	SELECT TIMEDIFF(NOW(), UTC_TIMESTAMP);
	-- OR/AND
	select @@global.time_zone;

If the above two give back a time difference of `00:00:00` or the time
zone of `+00:00` then your server is in UTC already. Mine wasn't, so I 
updated my _my.cnf_ file to set the `default-time-zone` property:

	[client]
	default-time-zone='+00:00'
	...

	[mysqld]
	default-time-zone='+00:00'

Sadly, this _still_ didn't fix my problem entirely, now instead of both 
sides of the `Date` being shifted, I was back to where I was before with 
a valid UTC on creation, and an incorrect returned value from what felt 
like the database. After some more thinking, I started wondering if the 
client's default parameters included automatically converting Date's from
the server's time to the recieving end. And sure enough, once I set the 
timezone on the application side:

	javaOptions in Test ++= Seq("-Dconfig.file=conf/test.conf", "-Duser.timezone=UTC")

	javaOptions in Runtime += "-Duser.timezone=UTC"

My issues disappeared. But setting the user.timezone is a bit drastic as
it affects _the entire JVM_. I [found another option] in the parameter lists
that _seems_ like it should fix my problem without having to specify the 
timezone at the JVM level, especially since it seems that [anorm doesn't 
set a calendar] which is good, as the answer on that S.O. question explicitly
says the trick only works with a null Calendar. But, like [one of the 
commenters] I was still getting the client conversion on reading the data
for some reason.

So for now, I'm going to set my JVM to run in UTC as that seems like the 
only thing that actually fixes the client-reading conversion problem. 
This isn't a bad thing, as if I were running this application on a "real" 
server and not just my local computer, I'd probably be running that box
on UTC anyway.





[java.util.Date]:https://docs.oracle.com/javase/8/docs/api/java/util/Date.html
[connector paramaters one can pass to the JDBC]:http://cs.wellesley.edu/~cs304/jdbc/connector-j.html#connector-j-reference
[accountable]:https://github.com/EdgeCaseBerg/accountable
[for ages]:http://stackoverflow.com/a/22126586/1808164
[pain to developers]:http://stackoverflow.com/a/1650406/1808164
[Instant]:https://docs.oracle.com/javase/8/docs/api/java/time/Instant.html
[MySQL Date type]:https://dev.mysql.com/doc/refman/5.5/en/datetime.html
[Anorm's parser]:https://github.com/playframework/playframework/blob/2.3.x/framework/src/anorm/src/main/scala/anorm/Column.scala#L247
[failing test]:https://github.com/EdgeCaseBerg/accountable/blob/master/test/service/ExpenseManagementServiceTest.scala#L64
[found another option]:http://stackoverflow.com/a/7610174/1808164
[anorm doesn't set a calendar]:https://github.com/playframework/playframework/blob/2.3.x/framework/src/anorm/src/main/scala/anorm/ToStatement.scala#L359
[one of the commenters]:https://stackoverflow.com/questions/7605953/how-to-change-mysql-timezone-in-java-connection#comment35959548_7610174