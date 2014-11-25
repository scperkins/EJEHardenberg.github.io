### Adding and Subtracting Days in Java

This is going to be a short post. But one which hopefully will provide a
reference point to anyone doing a quick google search. 

It is often very common to see SQL queries constrained by dates and ranges. 
For example, if you say: "Give me all the records within the past X days"
you might see mySQL people using `INTERVAL` and some other date functions. 
If you're a performance conscious person like me, you don't want to make 
mySQL compute an interval over and over again for each row (possible in 
some queries). Instead, you want to provide a hard value to test against. 
In java it's easy enough to do something like this:

	import java.util.*;

	Map params = new HashMap<String,Object>();
	int daysBack = -x; //x is whatever number you need

    Calendar cal = GregorianCalendar.getInstance();
    cal.add(Calendar.DAY_OF_YEAR, daysBack);
    params.put("afterDate", cal.getTime());

    //query using these params...

Another situation you might run into is when you want to retrieve records 
for up to the end of the month or beginning of a month. But months come 
in all days, shapes, and leap-year sizes! What to do? Java has you covered 
again:

	Timestamp timestamp = //...
	calendar.setTime(timestamp)
	calendar.add(Calendar.DAY_OF_MONTH,calendar.getActualMaximum(Calendar.DAY_OF_MONTH));

Another method I've seen suggested was to add one month, set the day to the first 
of the month, then subtract a day. While this will work 10/12 times, it will fail
on the first and last month since we'll end up changing the year as well. Of 
course you can set the year. But why go through all that hassle when you can just
use `getActualMaximum` and avoid the issue entirely?

If you want to set the first day of the month, it's a single change to a Calendar
object:

    calendar.set(Calendar.DAY_OF_MONTH, 1)


