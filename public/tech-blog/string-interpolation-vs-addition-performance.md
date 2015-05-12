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
much] besides it performing the operation on the tops of the stack, so
our only real option is to look into the [source code]. Looking at
ceval.c (In the Python folder) we can find the C code that will execute
when we reach any op code. For example, here's `BUILD_TUPLE` 

	case BUILD_TUPLE:
    	x = PyTuple_New(oparg);
        if (x != NULL) {
        	for (; --oparg >= 0;) {
        		w = POP();
            	PyTuple_SET_ITEM(x, oparg, w);
        	}
        	PUSH(x);
        	continue;
        }
        break;

The PyTuple_* functions are defined in the Objects folder, in
tupleobject.c and the tuples themselves are implemented as simple lists.
The performance of which is determined by the size of the list itself.
In the case of addStr4, N=2 in what is likely to be an O(N) operation
(If I'm reading tupleobject.c correctly). The `PyTuple_New` function is
swiftly followed by the items on the stack (from `LOAD_FAST`) being
placed into the tuple by `PyTuple_SET_ITEM`, this being a constant time
operation as it is simply pointer arithmetic under the hood:

	int
	PyTuple_SetItem(register PyObject *op, register Py_ssize_t i, PyObject
	*newitem)
	{
	    register PyObject *olditem;
	    register PyObject **p;
	    if (!PyTuple_Check(op) || op->ob_refcnt != 1) {
	        Py_XDECREF(newitem);
	        PyErr_BadInternalCall();
	        return -1;
	    }
	    if (i < 0 || i >= Py_SIZE(op)) {
	        Py_XDECREF(newitem);
	        PyErr_SetString(PyExc_IndexError,
	                        "tuple assignment index out of range");
	        return -1;
	    }
	    p = ((PyTupleObject *)op) -> ob_item + i;
	    olditem = *p;
	    *p = newitem;
	    Py_XDECREF(olditem);
	    return 0;
	}

Overall the build tuple function is, roughly, 2*O(N) or simply O(N)
where N is the size of the tuple. 

What about some other operations? Let's look at `BINARY_ADD`: 

    case BINARY_ADD:
        w = POP();
        v = TOP();
        if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
            /* INLINE: int + int */
            register long a, b, i;
            a = PyInt_AS_LONG(v);
            b = PyInt_AS_LONG(w);
            /* cast to avoid undefined behaviour
               on overflow */
            i = (long)((unsigned long)a + b);
            if ((i^a) < 0 && (i^b) < 0)
                goto slow_add;
            x = PyInt_FromLong(i);
        }
        else if (PyString_CheckExact(v) &&
                 PyString_CheckExact(w)) {
            x = string_concatenate(v, w, f, next_instr);
            /* string_concatenate consumed the ref to v */
            goto skip_decref_vx;
        }
        else {
          slow_add:
            x = PyNumber_Add(v, w);
        }
        Py_DECREF(v);
      skip_decref_vx:
        Py_DECREF(w);
        SET_TOP(x);
        if (x != NULL) continue;
        break;

Ok, so let's attempt to break this down a bit and understand it! The
`PyInt_CheckExact` is a simple macro defined in Include/intobject.h
which compares the object type to a reference of the `PyInt_Type`, so
nothing crazy or time consuming there. The code does basic arithmetic on
longs unless it's adding two strings or non-integers. The
`string_concatenate` function does different work depending on the next
instruction, fortunately in our case we're not doing any `STORE_`
operations, so we don't fall into any of the special cases defined
around line 4811 in ceval.c and the function does a small amount of
processing in order to add the two strings together. Taking the size of
the two strings and then using [memcpy] to quickly move the text over.
In other words, we'll count the string size (2 O(N) operations), then
copy the text into the newly allocated memory (another 2 O(N)
operations). 

Intuitively, we can now understand why multiple additions of strings
together might have a performance issue now. In the same way that java
allocates a new String object to do string concatenation (if you're
doing "" + "" in Java), Python has to move the strings into a new zone
of memory and copy them each time. Essentially the same way. In java, we
get around this issue (and in fact the JVM optimizes to this case:) by
using a [StringBuilder]. Which uses a list, much like our Tuple
Interpolation does. 

Finally, for completeness, let's look at `BINARY_MODULO`. 

    case BINARY_MODULO:
        w = POP();
        v = TOP();
        if (PyString_CheckExact(v))
            x = PyString_Format(v, w);
        else
            x = PyNumber_Remainder(v, w);
        Py_DECREF(v);
        Py_DECREF(w);
        SET_TOP(x);
        if (x != NULL) continue;
        break;

Surprised that it's shorter than the add function? Don't be! In our
case, the `PyString_CheckExact` returns true (this is the same type of
check as the Integer type check as before) and we run the
`PyString_Format` function on our two variables. This function is nearly
500 lines long and defined in Objects/stringobject.c on line 4226.
Despite it's length it's not actually _that_ complicated. It steps
through the string looking for a format specifier. In our case, we'll
skip the first 146 lines or so through if statements and end up at line
4440 where the `case 's':` is defined. 

Within this case (and falling through to the `r` case as well) we'll do
a few type checks before retrieving the variable as a string through the
`PyString_AS_STRING` macro. This macro does no error checking and is
quite fast. As noted by its definition in Include/stringobject.h:


	/* Macro, trading safety for speed */
	#define PyString_AS_STRING(op) (((PyStringObject *)(op))->ob_sval)

So long as our string isn't unicode, we'll use this fast version.
Otherwise we'll drop into the last 44 lines of the function and have to
do a bit of decoding and argument shifting with Tuples. Since we're just
talking about normal use cases with typical strings, we won't get into
this. And in short can say that we'll take one pass through the string
(with possible, but unlikely resizing), and have a constant time
operation to retrieve the string values of our values. 

A side note: The reason I sing unlikely resizing is because the length
of the initial buffer is:

	fmtcnt = PyString_GET_SIZE(format);
	reslen = rescnt = fmtcnt + 100;

Which will be 100 characters greater than whatever we've already put
into the formatter. If you're working with numbers or small strings,
then it's unlikely you'd hit this length. Even if you do, the
`_PyString_Resize` function (defined in Object/stringobject.c) uses
[realloc] under the hood so we don't need to copy the old string since
we're extending the memory to fit the requested size. In other words,
this method is going to be more efficient than the `BINARY_ADD` pretty
much always unless your machine has very little memory.

In conclusion, interpolating strings is faster than adding them
together. There is a caveat to this of course, in the case of a single
string adding to a single string, it wouldn't surprise me to see the
normal addition do better than the interpolation. This thought being
based off of the logic surrounding the formatting code being a bit
slower than a single copy from one call to `BINARY_ADD`. You can affirm
this behavior yourself by noting how as the number of arguments to
process increases, the better the interpolation code does versus the
addition. 

Feel free to clone [my example repository] and run the makefile to view
how the interpolation fairs on your machine compared to my results! It
would be interesting to see if different OS's or versions show
difference in this micro optimization.



[friend's code]:https://github.com/kiripaul/CS_125/blob/master/UTM/utm.py
[busy beaver]:https://en.wikipedia.org/wiki/Busy_beaver
[some people are]:http://legacy.python.org/workshops/1998-11/proceedings/papers/montanaro/montanaro.html
[simple enough]:http://www.electronics-tutorials.ws/combination/comb_7.html
[the documentation doesn't say much]:https://docs.python.org/2/library/dis.html#opcode-BINARY_MODULO
[source code]:https://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
[memcpy]:http://linux.die.net/man/3/memcpy
[StringBuilder]:https://docs.oracle.com/javase/7/docs/api/java/lang/StringBuilder.html
[realloc]:http://linux.die.net/man/3/realloc
[my example repository]:https://github.com/EdgeCaseBerg/python-str-playtime
