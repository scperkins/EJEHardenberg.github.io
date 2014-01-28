I've been playing around with C a lot in my spare time recently. Something I 
managed to run into last night was an interesting case of buffer overflow that
valgrind lovingly referred to as "stack smashing".

Let me layout some of the information for you:

We have, mysql interaction through a file called (cleverly) db.c. It's queries
are stored in it's header file as strings ready to have their %s, %08lu and 
%whathaveyou filled up by the information I sprintf (or snprintf) into them. 

Next up, we have a couple of structs that represent some of the tables in the
database. These are my models. Each model is pretty simple, simple fields, some
special methods to zero-out the memory used in the structures and a few functions
that format whatever data is given to them before storing it into the model.

Finally, we have the JSON helper file, which takes one of the model structures 
and then formats a JSON representation of it, once again, through some sprintf
activity. 

This is all pretty simple sounding. So where did it go wrong?

Oddly enough, in the JSON formatting. Here's what would happen:

- I'd make a model structure
- I'd insert it into the database
- I'd transform it into a JSON structure
- I'd print said JSON structure
- I'd attempt to delete the structure from the database
- A failed SQL query would occur
- The JSON would attempt to print out form the result of the query
- Stack Smash

When I saw the error messages, I began hunting around a bit for the problem near 
where the program had reported the smash -- at the end of the insertion function.

The strange thing was that it was reporting the last line of the function as the
area that was having a bad read. Confused I stared at my output for a little bit
before turning towards the mySQL error that had been reported above valgrind's
output and backtraces. 

Syntax error? I checked the query. No error there. So somehow I was introducing 
a syntax error into my query when inserting content. Well that sounds reasonable.

Except that the content being printed into the query was a sha256 hash. In ASCII
characters. So how the heck could there be a syntax error near a timestamp? 
(This was the reported error).

With nothing else to go off of in my log, I added logging to the query itself
within the function and was surprised to see that my sha256 hash had somehow
went from being 64 characters of ASCII to being part of the text stored in a 
different field of the struct.

Clearly something had gone wrong when I wrote the field in the structure right? 
I checked my functions and saw that I had very deliverately set the size of the
character buffers to safe sizes and that they shouldn't have overran.

Switching to trial and error mode I decided to print the offending field through
out the programs lifetime and figure out when it changed. I was made even more
confused when it was changed when the structure had been formatted for JSON use. 

I scanned my JSON formatting code. Added additional logging. Nothing went wrong
in the function it seemed. My program crashed and burned on exiting that function
though. Taking a second look, my last statement in the function was something
along the lines of

<pre> return sprintf(jsonOutput, "%formattinghere",bunch,of,variables) </pre>

Well, at least it made sense to accidently overrun a buffer during the use of
sprintf -- after all, sprintf is notorious for usage in buffer overflow attacks.

I increased the size of my jsonOutput variable and lo and behold all worked well.
Decreasing it down again resulted in a stack smash and a crash. Good! Reproducable
errors are the best kind. 


To actually fix the problem (besides increasing a buffer size) I'm re-coding my
formatting functions to all use snprintf and do some sanity checking on the lengths
of characters written before attempting to write into the output buffer. 

It's these kind's of problems that I love to be honest. Dealing with memory and
with primitive data types is probably one of my favorite things to do. 

