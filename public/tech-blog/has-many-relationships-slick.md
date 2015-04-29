### Handling Has Many Relationships with Slick 

Relational data is a normal thing to run into in web applications. And 
handling this data is often simple when dealing with single records or 
lists displaying a lot of content. But sometimes it can require a bit 
of thought to get our data in the form we want it to be. 

For example, consider the _Has Many_ relationship between two objects.
A simple parent-child relationship is expressed cleanly in SQL when 
parsed in two queries:

	SELECT id, datafield, andstuff FROM table1 WHERE id = 1;
	-- Returns one row
	SELECT id, otherdata, fId FROM table2 WHERE fId = 1;
	-- Returns multiple rows

The above are the type of queries that would be issued if your system 
did something like the following in pseudo code:

	function getTable1Obj(id)
		d = doDataBaseLookUp(id)
		return mapToApplicationObj(d)

	function enrichObjectWithTable2Info(obj)
		list = doDataBaseLookUp(obj.id)
		obj.table2Stuff = list
		return obj

If you're viewing a single object, then this is pretty normal and what 
one might expect to see in a simple application. After all, 2 queries 
isn't that many. But what about when we want a list of the information?

	SELECT id, datafield, andstuff FROM table1;
	-- Returns a bunch of rows
	SELECT id, otherdata, fId from [table2 WHERE fId = 1
	SELECT id, otherdata, fId from table2 WHERE fId = 2
	SELECT id, otherdata, fId from table2 WHERE fId = 3
	SELECT id, otherdata, fId from table2 WHERE fId = 4
	...

The above queries would be the case if our application code was doing 
something like this in pseudo code:

	for each object in table1:
		object = enrichObjectWithTable2Info(object)
		doStuffWithObject

What we've just ran into is called the [N+1 problem]. And it's pretty 
easy to get around if you know your databases. Specifically, the JOIN 
statement. We can pull back _all_ the information with a single query 
in _both_ cases:

	-- Case 1
	SELECT t1.id, t1.datafield, t1.andstuff, t2.id, t2.otherdata 
	FROM t1 JOIN t2 ON t1.id=t2.fId WHERE t1.id = 1
	-- Returns a bunch of rows
	-- Case 2
	SELECT t1.id, t1.datafield, t1.andstuff, t2.id, t2.otherdata,t2.fId 
	FROM t1 JOIN t2 ON t1.id=t2.fId
	-- Returns a bunch of rows 

This is great performance wise, but now we also need to deal with the 
fact that our application has to handle multiple rows and not just a 
single one anymore. For each row in t2, we'll have duplicate content 
from t1 in the records returned:

	| 1, "foo", "bar", 1, "boz", 1 |
	| 1, "foo", "bar", 2, "baz", 1 |
	| 1, "foo", "bar", 3, "bar", 1 |
	| 2, "fiz", "bar", 4, "boz", 2 |

If we're hoping to get a single Table1 object, with a field that has a 
list of Table2 objects, we'll need to aggregate the records in our code 
and assign them appropriately. To do this, we can turn to scala's great 
mapping functions. Let's assume we have a couple of case classes that 
slick is mapping to:

	case class T2(id: Int, otherdata: String, fId: Int)
	case class T1(id: Int, datafield: String, andstuff: String) {
		var t2s : Option[List[T2]] = None
	}
	

And that we're retrieving our data with a simple join like this:

	/* How you might query Slick for this: */
	for {
			r <- table1
			e <- table2 if e.fId === r.id
	} yield (r,e)

Since we're using `yield (r,e)` we'll end up with tuples of data 
that will look like this:

	val results = List(
		(T1(1, "foo", "bar"), T2(1,"boz",1)),
		(T1(1, "foo", "bar"), T2(2,"baz",1)),
		(T1(1, "foo", "bar"), T2(3,"bar",1)),
		(T1(2, "fiz", "bar"), T2(4,"boz",2))
	)

To map these into two objects (with id's 1 and 2) that have their 
table2 rows listed in the `t2s` field, we can use a couple functions 
from scala's collection framework. First off, we can use the convenient 
[groupBy] to break them down into a form like so:

	results.groupBy(_._1)
	/* Whose type is: 
		scala.collection.immutable.Map[T1,List[(T1, T2)]] = 
			Map(
				T1(2,fiz,bar) -> List(
					(T1(2,fiz,bar),T2(4,boz,2))
				), 
				T1(1,foo,bar) -> List(
					(T1(1,foo,bar),T2(1,boz,1)), 
					(T1(1,foo,bar),T2(2,baz,1)), 
					(T1(1,foo,bar),T2(3,bar,1))
				)
			)
	*/

This is already pretty close, all we really need to do is map over the 
collection and return the `T1` classes with the appropriate list: 

	results.groupBy(_._1).map {
		case (t1, tuples) => { 
			t1.t2s = Some(tuples.map(_._2))
			t1
		}
	}

Whose type is `immutable.Iterable[T1]`, we can convert this into a list 
by calling `toList` at the end, and then we'll be able to use the single 
object along with its children easily:

	> val t1s = results.groupBy(_._1).map {
		case (t1, tuples) => {
			t1.t2s = Some(tuples.map(_._2))
			t1
		}
	}.toList
	> t1s(1).t2s
	Option[List[T2]] = Some(List(T2(1,boz,1), T2(2,baz,1), T2(3,bar,1)))

There's not much to be said about this, we've grouped by the class T1 at 
first. With case classes, this means that the comparator is based on the 
items in the constructor (so `t2s` does not affect comparing two `T1`s) 
and we'll end up with a list of Tuples for the value and a `T1` for each 
key. Mapping over this we can get both key and value of the map by using 
the `case (t1, tuples)` statement. Traversing the tuples and collecting 
only the `T2`s is simple to do with another map inside the case 
statement.

You might be wondering, why are we using `Option[List[T2]]`? This is so 
we can implement performant look ups via a pattern I've started using 
in my own work:

	case class T1(id: Int) {
		var someChild : Option[List[Child]] = None
		def getChild() = {
			if(!someChild.isDefined) {
				Child.getById(this.id)
			}
			someChild
		}
	}

The benefit to this pattern is that you can retrieve a single object 
from the database, then only get the children if you need them. (This 
is the two query approach), but you can also use a join statement and 
assign the children to the object (as we've done above) and then still 
call `getChild` and it will *not* go to the database.

This is beneficial because your client code for your view only ever calls 
a single method `getChild` and you don't have to worry about if your 
data came from a join statement, or hasn't shown up yet. If you're not 
careful you will end up with an N+1 problem, but so long as you are mapping 
appropriately you won't hit it and can aggregate the joined information 
onto the parent side of the relationship in one shot.

As a final tip, it can quickly become unreadable as you join more and 
more tables. Therefore it is wise to abstract your aggregation 
functions into seperate helper methods like so:

	private def _aggChildrenFromJoinToParent(t1: Recipe, tuples: List[(T1, T2)]) = {
		t1.t2s = Some(tuples.map(_._2))
		t1
	}
	private def aggChildrenFromJoinToParent = (_aggChildrenFromJoinToParent _).tupled

And then you can use it like so:

	val t1s = results.groupBy(_._1).map(aggChildrenFromJoinToParent).toList

This is more readable if you have a large amount of mapping or child 
objects. What's going on is you are "tupling" the function. Treating 
the function as a partially applied function and then using it in place 
of the case statement.


[N+1 problem]:http://stackoverflow.com/a/97253/1808164
[groupBy]:http://www.scala-lang.org/api/2.10.3/index.html#scala.collection.immutable.List