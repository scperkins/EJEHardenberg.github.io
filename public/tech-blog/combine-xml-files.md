### Let's combine XML files! (with bash)

Today I was thinking of ways to improve my bash skills when a simple task 
appeared for me. Combine two XML files together. Same type, same xsd to 
validate the two. A simple approach would be to open up the files and 
copy paste the contents of one to the other. But thinking programatically 
I realized there were some simpler ways (and faster when working with 
large files).

#### Sample XML:

sample.xml

	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd">
	        <TestInfo>
	                <Id>1</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Monday</Day>
	                </Days>
	        </TestInfo>
	</TestInfoList>

sample2.xml

	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd">
	        <TestInfo>
	                <Id>2</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Friday</Day>
	                </Days>
	        </TestInfo>
	</TestInfoList>

#### Thought process

Because we know that our two files are similar, we really just need to 
work at the outer tag layer. Thinking about this from the stance of copying 
and pasting manually, we would do something like the following:

1. Copy the first file to a another
2. Remove the closing `</TestInfoList>` tag
3. Copy the second file, sans the first opening tag to the other

This can be translated into bash via simple `head` and `tail` calls. The `head`
command allows us to take the first `n` lines of a file, and the `tail` the 
last `n` lines of a file. We can then translate our above process to:

1. Take the head of the file, up to the number of lines in the file -1
2. Take the tail of the second file, up to the number of lines in the file -2

Assuming that there isn't any new lines at the end of the file, this will work 
fine. 

#### head, tail, and bash

We can use the `wc` program to count the words in a file, but given the switch 
`-l` it will count the number of lines instead. So we can get the number of lines 
in a file simply by executing `wc -l >file>` which will print out the number of 
linesand the filename. However, if we _pipe_ the file to `wc` we'll only get the 
number of lines:

	$ wc -l < sample.xml 
	13

Bash allows simple arithmetic as well. So we can combine this with the line count
like so:

	$ echo $(($(cat sample.xml | wc -l)-1))
	12

Next, using this number we can pass it to the `tail` or `head` command via the 
`-n`. Simple right?


	$ head -n $(($(cat sample.xml | wc -l)-1)) sample.xml 
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd">
	    <TestInfo>
	            <Id>1</Id>
	            <Name>Name</Name>
	            <Days>
	                <Day>Monday</Day>
	            </Days>
	    </TestInfo>

this gives us the first half of our XML. The second half is easily gotten from 
tail:

	$ tail -n $(($(cat sample2.xml | wc -l)-2)) sample2.xml 
        <TestInfo>
                <Id>2</Id>
                <Name>Name</Name>
                <Days>
                    <Day>Friday</Day>
                </Days>
        </TestInfo>
	</TestInfoList>

If we wanted to do both of these commands at once we can use `echo`:

	$ echo $(head -n $(($(cat sample.xml | wc -l)-1)) sample.xml) $(tail -n $(($(cat sample2.xml | wc -l)-2)) sample2.xml )
	<?xml version="1.0" encoding="UTF-8"?> <TestInfoList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd"> <TestInfo> <Id>1</Id> <Name>Name</Name> <Days> <Day>Monday</Day> </Days> </TestInfo> <TestInfo> <Id>2</Id> <Name>Name</Name> <Days> <Day>Friday</Day> </Days> </TestInfo> </TestInfoList>

Granted this does squish everything together. The XML is still vaild. If we 
wanted to preserve the formatting, we'd want to use temporary files:

	 head -n $(($(cat sample.xml | wc -l)-1)) sample.xml > t1; tail -n $(($(cat sample2.xml | wc -l)-2)) sample2.xml > t2; cat t1 t2 > t3; rm t1 t2;

And then t3 will hold the output:

	cat t3 
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd">
	        <TestInfo>
	                <Id>1</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Monday</Day>
	                </Days>
	        </TestInfo>
	        <TestInfo>
	                <Id>2</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Friday</Day>
	                </Days>
	        </TestInfo>
	</TestInfoList>

#### More?

Assuming that your XML files are simple and have 1 line at the start for 
their xml version string, then another line for the schema, this strategy
will work fine. What about when it's more than two files though? We can 
obviously write out the steps, but it will become apparent that we can 
simply work in pairs and build up an xml file incrementaly. Or, we can 
do something a bit smarter. If we think of an xml file as a header, footer,
and body then our task becomes much simpler. We need a single header (composed 
of the version, schema, and openning tag) and a single footer (the closing tag 
of the element list). These two things stay constant. 

Header:

	head -n 3 file

Footer:
	
	tail -n 1 file

And the body? Well the body is just everything between! We can get that 
using head and tail to strip away the header and footer. All in all, we'd
end up with something like this:

	#add conditional logic to check for > 1 params
	#Take the version, schema, and opening tag
	head -n 2 $1

	for i in $*
	do
		head -n $(($(cat $i | wc -l)-1)) $i > /tmp/t1;
		tail -n $(($(cat /tmp/t1 | wc -l)-2)) /tmp/t1 ;
		rm /tmp/t1;
	done;

	#Take the last line
	tail -n 1 $1

In action:

	$ sh combine.sh sample.xml sample2.xml sample3.xml 
	<?xml version="1.0" encoding="UTF-8"?>
	<TestInfoList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://localhost:9000/testInfo.xsd">
	        <TestInfo>
	                <Id>1</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Monday</Day>
	                </Days>
	        </TestInfo>
	        <TestInfo>
	                <Id>2</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Friday</Day>
	                </Days>
	        </TestInfo>
	        <TestInfo>
	                <Id>1</Id>
	                <Name>Name</Name>
	                <Days>
	                    <Day>Wednesday</Day>
	                </Days>
	        </TestInfo>
	</TestInfoList>

#### Limitations

Obviously, this scripting relies on a very simple XML scheme, and uniform 
content as far as newlines go. If we didn't have this, we'd probably want
to script something with actual XML support and not just manipulate the 
files via bash. Regardless, I had fun playing with bash and I hope this 
has inspired you to have a bit of fun with it yourself. 