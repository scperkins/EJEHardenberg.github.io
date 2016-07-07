### Getting a String _before_ another in MySQL

The other day I had a bit of a fun problem to solve. We had some data in 
MySQL, all stored, unfortunately, in a denormalized, and hell, blobby 
way. So instead of seperated fields for a set of data points, they were 
all stuck into a single text column. The problem to solve was to take 
a string to find, and then return it and the string _before it_ until it 
found another keyword. 

So for an example let's say we have:

	<blob>
		<blobThing>
			<data>This is just some dummy data</data>
			<tidbit>This is some cool data</tidbit>
		</blobThing>
		<blobThing>
			<data>This is just some other dummy data</data>
			<tidbit>This is some lame data</tidbit>
		</blobThing>
		<blobThing>
			<data>This is just some more dummy data</data>
			<tidbit>This is some other data</tidbit>
		</blobThing>
	</blob>

<small>And yeah, XML? In a database? Terrible and horrible idea I'm aware, but 
hey, when you're given stuff to deal with, you gotta just deal with it
sometimes.</small>

If we wanted to extract the `data` and its `tidbit` based on information in 
the `tidbit`, we would need to find the tidbit, then backtrack to the 
closest opening `data` tag. Unfortunately, MySQL doesn't really have that 
ability in one handy function like it does [other things]. Still, with 
some creative use of a few of the other string functions, we can arrive 
at a solution that works well enough to get by in our extraction.

Let's say we want the middle `data` and `tidbit`, we know that the `tidbit`
has "lame data", so we can find that using the [LOCATE] if we wanted to, 
but I'm going to (out of preference really) use the [INSTR] method since 
it reads easier to me to have the subject as the first argument:

	INSTR(myColumn, 'lame data</tidbit>');

From here, we now face the real crux of the issue, which is, how do we get 
the stuff before the index we just found? If we use `SUBSTR` now we'll only 
get up to what we found with `INSTR`:

	<blob>
		<blobThing>
			<data>This is just some dummy data</data>
			<tidbit>This is some cool data</tidbit>
		</blobThing>
		<blobThing>
			<data>This is just some other dummy data</data>
			<tidbit>This is some lame data</tidbit>

We can't use `INSTR(myColumn, <data>)` to find the previous `data` element 
since that would find us the first on in the string. So what we need to 
do is make the previous `data` element the first `data` element in the 
string. To do this, we just have to think and understand that if we 
consider that we've cut our string down to the last `tidbit` we needed, 
then if we flipped the string, the first open `data` element would be the
one we need!

	REVERSE(
		SUBSTRING(
			myColumn FROM 1 FOR 
			INSTR(myColumn, 'lame data</tidbit>') + LENGTH('lame data</tidbit>') -1
		)
	)

Doing something like the above gets us the slightly uncomprehensible:

			>tibdit/<atad emal emos si sihT>tibdit<
			>atad/<atad ymmud rehto emos tsuj si sihT>atad<
		>gnihTbolb<
		>gnihTbolb/<
			>tibdit/<atad looc emos si sihT>tibdit<
			>atad/<atad ymmud emos tsuj si sihT>atad<
		>gnihTbolb<
		>bolb<

Now, to find the first open data element we need to use `INSTR` with the 
reversed string of what we want:

	INSTR(<the above string>, REVERSE('<data>'))

This gives us the index within the _reversed_ substring we need to get 
to. To extract the text from our reversed string we can then use 
`SUBSTRING` and the indices we now have:
	
	SUBSTRING(
		REVERSE(
			SUBSTRING(
				myColumn FROM 1 FOR 
				INSTR(myColumn, 'lame data</tidbit>') + LENGTH('lame data</tidbit>') -1
			)
		), -- This is Just our reversed bit from before
		1, -- Start at the beginning of the reversed string because it starts at what we found before
		INSTR(
			REVERSE(
				SUBSTRING(
					myColumn FROM 1 FOR 
					INSTR(myColumn, 'lame data</tidbit>') + LENGTH('lame data</tidbit>') -1
				)
			),
			REVERSE('<data>') -- Grab the index of where the first open data element before our lame data</tidbit> is
		) + LENGTH('<data>') -- Capture the tag as well 
	)

We're close now, the above will net you:

	>tibdit/<atad emal emos si sihT>tibdit<
	>atad/<atad ymmud rehto emos tsuj si sihT>

Which just needs to be put through `REVERSE`

	<data>This is just some other dummy data</data>
	<tidbit>This is some lame data</tidbit>

And there you have it! Of course, this works well with data like XML or 
other things you probably really shouldn't be storing in a database anyway. 
But like I said, beggers can't be curious. You could still use this to 
deal with non structured data as well if you know your data well. For
example:

	Once upon a time there was a fish, and it was really neat
	and I have no idea what to put here but hey it's dummy data!

in a column could have the last part pulled out with:

	REVERSE(
		SUBSTRING(
			REVERSE(
				SUBSTRING(
					myColumn FROM 1 FOR 
					INSTR(myColumn, 'dummy data') + LENGTH('dummy data') -1
				)
			),
			1,
			INSTR(
				REVERSE(
					SUBSTRING(
						myColumn FROM 1 FOR 
						INSTR(myColumn, 'dummy data') + LENGTH('dummy data') -1
					)
				),
				REVERSE('I ')
			) + LENGTH('I ')
		)
	)

To get:

	I have no idea what to put here but hey it's dummy data

If the string you're looking for _isn't_ in the data, then you're going to get 
back some funny results trying to do this whole thing all at once. So it would 
be better to write a stored procedure or function that would handle the cases 
where the `INSTR` methods don't find what you're looking for.



[other things]:https://dev.mysql.com/doc/refman/5.7/en/string-functions.html
[LOCATE]:https://dev.mysql.com/doc/refman/5.7/en/string-functions.html#function_locate
[INSTR]:https://dev.mysql.com/doc/refman/5.7/en/string-functions.html#function_instr