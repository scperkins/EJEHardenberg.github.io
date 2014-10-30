### Order by Random in MySQL (without starting at 1) 

The classic tale of `ORDER BY RAND` is one which many programmers find
themselves running into. Quickly after attempting, they find themselves
in heaps of trouble with database queries piling up as rows upon rows
are shuffled about only to return a single record as output. 

There are [many](http://jan.kneschke.de/projects/mysql/order-by-rand/),
[many](http://mihasya.com/blog/pull-random-data-out-of-mysql-without-making-it-cry-using-and-optimizing-order-by-limit-offset-etc/),
blogs on the subject already. Something these fail to address though is
the situation where your id's (assuming you've got a numeric `AUTO_INCREMENT` id) 
don't start at one. The first link mentions dealing with gaps in the id's 
of your record set; but it uses another table to do so, becuase it assumes that you've deleted
random rows in your set and therefore no long have an ordered list.

What about this situation?

You've been testing out code, deleting all the rows as a whole at the 
end of each run, and now have an id that starts at 45663 and ends at 
47321. The method described in many blogs is typically similar to this:

	SELECT * FROM 
		table r1 JOIN
		(SELECT CEIL(RAND() * 
			(SELECT MAX(id) FROM table)) AS id
		) r2
	WHERE r1.id >= r2.id
    ORDER BY r1.id ASC 

Which **will** work if you have a wide distribution of ids. But if you have
a densely populated set of numbers sitting at the extremes of your set,
then you're likely to get the same Id over and over again.

So how do you fix it? Simple, instead of using `RAND() * MAX(ID)` use
`MAX(ID) - MIN(ID)` to retrieve roughly how many numbers there are in 
your table and then add a random number from that range to your base id.

	SELECT * FROM 
		table f JOIN 
		(SELECT MIN(id) + (
			(MAX(id) - MIN(id))*RAND()
			) AS 'rid' FROM table) b 
		ON f.id >= b.rid
	ORDER BY f.id ASC

Once you do this you no longer have to worry about where your Id starts,
and can safely delete every row in a table without having to reset and 
rely on your `AUTO_INCREMENT` id starting from 1. 

