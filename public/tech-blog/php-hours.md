### Listing Hours for Business's with PHP

#### A fun problem

Today I was working on a website that needed to display human readable hours for
businesses. In addition, I needed to make a simple administrative interface as 
well. During this process I got to solve one of those problems you might run into
during an interview.

*Given a list of numbers, find sequences of "upruns" in the list*

By an uprun, I mean something like: 1,2,3 or 2,3,4, but not 2,4,5 or something
that has what I'll call a gap in it.

Believe you see the solution, think about it for a minute and see if your intuition
can find an N-time algorithm to do so. ... Ready? 

#### Finding sequences

To find an uprun within a list it is easy enough to recognize that if you are 
looking through a list of numbers, the difference between each number in a sequence
should be 1. Using this knowledge it's rather obvious to see how we might process 
the following list:

    List: 1,2,3,5,6,7
    Diff: 0,1,1,2,1,1 
               or
          0,1,2,1,1,1 

And note that the start of the second sequence is where the difference between 
the current number and its predecessor is greater than 1, or where the successor 
of the current number is greater than 1.

This works, but is there another way? Yes! On observation, we can also see that 
since the list is in order, the number at the _i_<sup>th</sup> place's value, 
minus one, should be equal to the value of the previous number. Or, visually:

    List:  1,2,3,5,6,7
    Equal: x T T F T T

We don't have a predecessor for the first element, so we can ignore it, but you'll
see that when _2_ is our current number, then _2-1=1_ which is the value of the 
previous list element. Moving on, you can see that at the start of the second 
sequence _5-1=4_ which is not equal to the previous element _3_.

Both of these methods are valid. The implementation below uses the
second strategy:

	<?php

	function humanDayList($daylist){
		$daylistNums = explode('.',$daylist);
		sort($daylistNums);
		$seq = 0;
		$sequences = array();
		for ($i=0; $i < count($daylistNums); $i++) { 
			if($i == 0){
				$seq = 0;
				continue;
			}
			/* If there is a gap then note it */
			if( $daylistNums[$i] -1 != $daylistNums[$i -1] ){
				$sequences[] = array($seq, $i -1);
				$seq = $i;
			}
		}
		$sequences[] = array($seq, count($daylistNums)-1);

		/* Convert Sequences into the days string */
		$dayStrs = array("Sun","Mon","Tue","Wed","Thu","Fri","Sat");
		$daylistStrings = array();
		foreach ($sequences as $sequence) {
			$start = $sequence[0];
			$end = $sequence[1];
			if($start == $end){
				$daylistStrings[] = $dayStrs[$daylistNums[$start]];
			}else{
				$daylistStrings[] = $dayStrs[$daylistNums[$start]] . '-' . $dayStrs[$daylistNums[$end]];
			}
		}

		return implode(',', $daylistStrings);

	}
	?>

The input to this function is a list of numbers (0-6) seperated by
periods. The output is something like: "Sun-Mon,Wed,Fri-Sat" depending
on the list. Here are some example runs:

	'0.1.3.5.6' => Sun-Mon,Wed,Fri-Sat
	'0.1.2.3.4.5.6' => Sun-Sat
	'0.2.4.6' => Sun,Tue,Thu,Sat

#### But what about hours?

Using this it is not only easy to construct sequences for each schedule
for a business, but easy to search a database field to determine if a
business has hours on a certain day. Just by using the php function
`date('G')` you can get the index for the day and do a simple text
search. 

But of course, when a business lists its hours, it looks something like
this:

*Ethan's Amazing Business*
*Mon-Fri: 9:00am - 5:30pm*

or something similar. Which means we probably also want to store the
hours of a business for whatever range of days it is valid for. In other
words, we need a way to represent the time of day. And preferably, since
we're constructing a useful tool, the representation will still allow
for database queries to find out if a business is open or not. 

The simplest way to do this is to represent the start and end times as
the number of minutes past midnight. You might ask yourself: "Why not just
represent them as hours?" to which I say: _what about 9:30?_ or any other
oddball time? Also, by using minutes you can use `date('g')` and `date('i')` 
to grab the current time and with a bit of math search for business within
certain hours easily. 

Once you have a start and end time in minutes, you can then use `mktime` 
and `date` to create the neccesary time string:

	<?php

	function hours($stime, $etime){
		if($stime > $etime){ //protect yourself from sillys
			$tmp = $etime;
			$etime = $stime;
			$stime = $tmp;
		}
		return date('g:ia',mktime($stime/60,$stime%60)) . '-' . date('g:ia',mktime($etime/60,$etime%60));
	}

	?>

With these two functions in place we can now easily show a business's 
operating hours. As far as database table structure goes:

    +-------------+---------------------+------+-----+---------+----------------+
    | Field       | Type                | Null | Key | Default | Extra          |
    +-------------+---------------------+------+-----+---------+----------------+
    | ID          | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
    | business_id | bigint(20) unsigned | NO   | MUL | NULL    |                |
    | daylist     | varchar(16)         | NO   | MUL | NULL    |                |
    | stime       | int(4)              | NO   |     | NULL    |                |
    | etime       | int(4)              | NO   |     | NULL    |                |
    +-------------+---------------------+------+-----+---------+----------------+

I'll update this post once I figure out some good index's and querys for efficient
querying of large pieces of data. For the average use case this is perfectly fine
though, becuase you're likely to be joining via a business id when displaying 
hours.

Searches like: 

	SELECT * FROM business_hours WHERE stime < x and x < etime -- where x is a number
	SELECT * FROM business_hours WHERE daylist LIKE %D% -- where D is a number for day
	SELECT * FROM business_hours WHERE daylist LIKE %D% AND stime < x AND x < etime

are going to be useful for filtering or sorting. If scaling, it might be wise to
implement something more efficient than using `Like %%`though.

#### Why store the days like that?

You might be asking yourself, why would we store the days as `d.d.d.d.d` or something
similar? The answer is for interface purposes it's much easier. If you're an admin
you don't want to select ranges from dropdowns or non-intuitive things like that.
You're going to want to be able to click a button for each day, or drag your cursor 
over some type of range mechanism. It's extremely simple javascript to convert a
list of selected buttons to a list of numbers seperated by dots. Not too mention 
that by representing the days in this way we can easily `explode` on the delimiters 
and easily use the ideas of sequences for finding the appropriate text.


