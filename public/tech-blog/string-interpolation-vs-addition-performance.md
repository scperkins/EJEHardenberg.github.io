### Which is faster? String Interpolation or Addition (in Python)? 

There comes a time in every young girls life where she asks the age old
question: "Which one of these methods of doing string operations is
more performant?" 

Okay, so maybe not every child in the world is asking these questions,
but I am. And after briefly critiquing a [friend's code] and hearing
about the performance issues he had fixed and worked with I got to
thinking. Well, actually it was a different friend jokingly calling the
code academic and not enterprise that made me look twice. 

For whatever reason, I honed in on the use of string addition, namely:

	print("          >>>>>>>>>>>>> Start String: "+self.final_tape+" <<<<<<<<<<<<<<<")

Where I was left wondering if the use of two strings and a variable
would be very different from the use of a single string and an
_interpolation of a variable_. My intuition told me interpolation would
be faster. 

Hoping to prove this to myself, I asked my friend to change his code
(and trust me he was so pleased to touch month old code again -- not) to
use string interpolation to find out. His [busy beaver] code was a good
way to see if there was a performance difference. His results? 

Interpolation: 1 minute 8 seconds  
Addition: 1 minute 11 seconds

So not much of a difference really, but a difference. So the next
question is why? The best way to find out is to ask the code! 

<script src="https://gist.github.com/EdgeCaseBerg/fc93d67b9279402c7211.js"></script>

As you can see in the gist, the addition function has 3 loads, 2 adds
and then the return. While the interpolation method has 2 loads, 1
module and 1 return. While it's only 2 operations difference, it does
make a difference if the code is in a critical path. It also makes a
difference depending on how many strings we are stringing together
(excuse the pun). 

	>>> def addStr3(s,s2):
	...     return ">" + s + ":" + s2 + "<"
	... 
	>>> def addStr4(s,s2):
	...     return ">%s:%s<" % (s,s2)
	... 
	
	>>> dis.dis(addStr3)
	  2           0 LOAD_CONST               1 ('>')
	              3 LOAD_FAST                0 (s)
	              6 BINARY_ADD          
	              7 LOAD_CONST               2 (':')
	             10 BINARY_ADD          
	             11 LOAD_FAST                1 (s2)
	             14 BINARY_ADD          
	             15 LOAD_CONST               3 ('<')
	             18 BINARY_ADD          
	             19 RETURN_VALUE        
	>>> dis.dis(addStr4)
	  2           0 LOAD_CONST               1 ('>%s:%s<')
	              3 LOAD_FAST                0 (s)
	              6 LOAD_FAST                1 (s2)
	              9 BUILD_TUPLE              2
	             12 BINARY_MODULO       
	             13 RETURN_VALUE        

As you can see, If we are trying to put in 2 variable strings with text
inbetween we'll end up with 5 loads, 4 adds, and 1 return in the
addition case. But the interpolation case, with 3 loads, 1 tuple build,
and 1 modulo and return has increased only by 2 operations. Compared to
the increase from 6 to 10 operations, this is a big deal for micro
optimizations. 

Continuing further, the question begs to be asked, is it a sequence?
After all, computers do things by the book and we can expect
instructions to be compiled down to op codes consistently. So adding yet
another variable in should result in similar results:

	>>> def addStr5(s,s2,s3):
	...     return ">"+s+":"+s2+":"+s3+"<"
	... 
	>>> def addStr6(s,s2,s3):
	...     return ">%s:%s:%s<" % (s,s2,s3)
	... 
	>>> dis.dis(addStr5)
	  2           0 LOAD_CONST               1 ('>')
	              3 LOAD_FAST                0 (s)
	              6 BINARY_ADD          
	              7 LOAD_CONST               2 (':')
	             10 BINARY_ADD          
	             11 LOAD_FAST                1 (s2)
	             14 BINARY_ADD          
	             15 LOAD_CONST               2 (':')
	             18 BINARY_ADD          
	             19 LOAD_FAST                2 (s3)
	             22 BINARY_ADD          
	             23 LOAD_CONST               3 ('<')
	             26 BINARY_ADD          
	             27 RETURN_VALUE        
	>>> dis.dis(addStr6)
	  2           0 LOAD_CONST               1 ('>%s:%s:%s<')
	              3 LOAD_FAST                0 (s)
	              6 LOAD_FAST                1 (s2)
	              9 LOAD_FAST                2 (s3)
	             12 BUILD_TUPLE              3
	             15 BINARY_MODULO       
	             16 RETURN_VALUE        

This time, the addition function uses 7 loads, 6 adds, and 1 return and
the interpolation functions uses 4 loads, 1 tuple build, 1 modulo, and 1
return. It should be fairly obvious at this point that each additional
string, if continued in the way we're adding the string in, will result
in 4 additional operations for the addition case, and 1 for the
interpolation. 

	Total Operations
	-----------------
	Add 	Interpolate
	6 		4
	10 		5
	14  	6 

This does not neccesary mean that interpolation is faster though! The
number of operations doesn't matter if one of those is a blocking or
long process. So what we really need to do is compare similarities and
diffferences between the operations. How many `LOAD_CONST`? `LOAD_FAST`?
What's the difference between `BINARY_ADD` vs `BINARY_MODULO`? How long
does it take to `BUILD_TUPLE`?

Unfortunately, I'm not as familiar with Python OpCodes as [some people
are]. I can see that a peephole optimizer might be able to make the
interpolated code even faster by replacing the `LOAD_FAST` in a row with
`LOAD_TWO_FAST` to load the variables faster. The key questions of
comparing Binary Add to Binary Modulo is a bigger issue though. So let
us consider how the two are implemented. Binary Add is [simple enough],
simply add each bit, then possibly carry a 1 over. The computer does
this with an AND gate and an XOR gate for each bit. While there are
likely plenty of optimizations and clever tricks used in today's
computers, it's semi-safe to assume that the `BINARY_ADD` will hit each
group of bytes with a few operations per bit to add the two areas of
memory together. 

So, what about `BINARY_MODULO`? Well, [the documentation doesn't say
much] besides it performing the operation on the tops of the stack
(hence binary). 

TODO: look into python source for implementation details?
[friend's code]:https://github.com/kiripaul/CS_125/blob/master/UTM/utm.py
[busy beaver]:https://en.wikipedia.org/wiki/Busy_beaver
[some people are]:http://legacy.python.org/workshops/1998-11/proceedings/papers/montanaro/montanaro.html
[simple enough]:http://www.electronics-tutorials.ws/combination/comb_7.html
[the documentation doesn't say much]:https://docs.python.org/2/library/dis.html#opcode-BINARY_MODULO
