### Ambiguous Columns with Java NamedParameterJdbcTemplate and Order By Clauses

Sometime you have queries that Join two tables together that share a column name. When selecting an `ORDER BY` clause for your statement, in order to use the shared column name you must specify which of the two table's column will be used. For example:


**Table A**

    id | foo | bar | baz

**Table B**

    id | bar | baz | boz

**Query**

	SELECT * FROM A a JOIN B b ON a.id = b.id ORDER BY a.bar

Note how we must say `a.bar`, otherwise mySQL will complain about the column being ambiguous since it is. In our application let's say that the user can filter results from A and B and arrange things by any column. So using a [NamedParameterJdbcTemplate] we'll have a query like so:

**Parameterized Query**

	SELECT * FROM A a JOIN Bb ON a.id = b.id ORDER BY :order

Attempts to set up your parameter map like so will fail:

	Map<String, Object> parameters = new HashMap<String, Object>();
	String order = //set to baz,boz,foo,bar, or id
	parameters.put("order", order);

	namedParameterJdbcTemplate.query( query, parameters, ...); //fail

Because if you pass in baz or bar for `:order` then you'll end up with an
ambiguous column error. So you might try to change it up by doing this:

**Still the wrong Query**

	SELECT * FROM A a JOIN Bb ON a.id = b.id ORDER BY a.:order	

Which will fail again with an error implying you need to qoute the value.

**_Still_ the wrong Query**

	SELECT * FROM A a JOIN Bb ON a.id = b.id ORDER BY `a`.`:order`

only now it will fail because the parameter `order\`` doesn't exist. 

So what do you do? Simple, use our original query and pass the tablename to
disambiguate the clause:

**The right way**

	String query = "SELECT * FROM A a JOIN Bb ON a.id = b.id ORDER BY :order"
	Map<String, Object> parameters = new HashMap<String, Object>();
	String order = //set to baz,boz,foo,bar, or id
	parameters.put("order", "a." + order); //note table name addition
	namedParameterJdbcTemplate.query( query, parameters, ...); //success!

Hope this helps someone else out there.

[NamedParameterJdbcTemplate]:http://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/jdbc/core/namedparam/NamedParameterJdbcTemplate.html