### Approaching Optimizations

About a week ago [my friend Phelan] sent me an email where he asked me to 
look at some code he had been working on. Specifically, a [Hacker Rank 
challenge about unfairness]. He told me that he had a solution to 
the problem, but it ran in about 30 seconds instead of 10 as the 
challenge required. 

Before he emailed me, he had thought he [already optimized] the code a 
little bit by removing a call to the `len` function and had presented 
me with the code below: 
	
	def compute_min_diff(n, k, candies):
		'''
			You can profile your program by doing something like this:
				cat sample_input | python -m cProfile max_min.py
			to identify the bottlenecks.
		'''
		min_diff = None
	
		for i in range(n): 
			subgroup = candies[i: i + k] 
			if len(subgroup) ==  k: 
				diff = subgroup[-1] - subgroup[0] # since list is sorted, max is last element and min is first
				if not min_diff or diff < min_diff:
					min_diff = diff
	
		return min_diff

Take a moment and see if you can spot a few places where one could improve 
the code to be more inefficient (or wait a moment and keep reading). After 
I had sent back my thoughts to him and he whittled the time down to 10 
seconds, he sent me a follow up email:

<blockquote>
	"I have a blog request for you to write! something along the lines of algorithm optimization, 
	like what you did to help me solve that hackerrank puzzle 
	(reasoning behind the steps you took, your thought process, etc...)

	just a thought!""
</blockquote>

While I normally write up small posts about little code problems I'm solving 
or projects I'm working on, it seems like a good change of pace to talk about 
how one approaches a problem like this. After all, people love things that 
go fast (and marketing says faster = $$$), so here we go:

#### Lists? SubGroups?

The first thing that pops out to me is the fact that we're considering 
subgroups of a list. If you put your computer hat on for a second and 
consider the first few lines you might notice something:

	for i in range(n): 
		subgroup = candies[i: i + k] 
		if len(subgroup) ==  k: #...

Specifically that we don't have to loop over the _entire_ list. A small 
micro optimization we can realize is that since each subgroup is of size `k`
and we create these groups from `i`, eventually we'll hit the case where the 
are less than `k` elements left in the list, at which the `len(subgroup) == k` 
will always be false. This is a _very_ small optimization if `k` is small, 
but still, it adds to performance since we loop over less, and we remove 
the `if` check entirely:

	def compute_min_diff(n, k, candies):
		'''
			You can profile your program by doing something like this:
				cat sample_input | python -m cProfile max_min.py
			to identify the bottlenecks.
		'''
		min_diff = None
	
		for i in range(n - k): 
			subgroup = candies[i: i + k] 
			diff = subgroup[-1] - subgroup[0] # since list is sorted, max is last element and min is first
			if not min_diff or diff < min_diff:
				min_diff = diff
	
		return min_diff

#### Faster! Faster!

So the code is now a faster, but it can still be made better. This is 
done by an observation of the `main` function of the program:

	def main():
		n = input() # the number of items in the list, passed in on stdin
		k = input() # the number of integers from the list we want to select
	
		candies = [input() for _ in range(0,n)]
		candies.sort()
	
		min_diff = compute_min_diff(n, k, candies)
	
		print min_diff

Notice the `candies.sort()`? That means our list is sorted when it comes 
into the `compute_min_diff` function. That means more optimizations! Next 
up, the subgroups, consider these two lines for a moment:

	subgroup = candies[i: i + k] 
	diff = subgroup[-1] - subgroup[0] # since list is sorted, max is last element and min is first

Any ideas? Remember that the elements are _sorted_. Oh, and Phelans comment 
is really the key here. Notice that we're taking a [slice] of the list. 
In other words, we're creating an object of just the subgroup we're looking 
at, that is, the subgroup from `i` to `i + k`. But, if the list is sorted 
and the max and min are the last and first elements at `i` and  `i + k`, 
why should we bother storing the data structure in the first place? 

The answer of course, is that it's easier for a programmer to read, but 
when it comes to optimizing, readability sometimes goes out the window. 
But by doing so, we free ourselves of the computations to slice the list 
and also the space to store it, replacing it with two simple numbers. Thus 
our two lines of code become one more efficient one:

	diff = candies[(i+k)-1] - candies[i]

Replacing objects that take up space and the computations needed to create 
them with two constant time operations is _much_ better for performance. 
So at the end, Phelan had the following solution for the problem: 

	def compute_min_diff(n, k, candies):
		'''
			You can profile your program by doing something like this:
				cat sample_input | python -m cProfile max_min.py
			to identify the bottlenecks.
		'''
		min_diff = None
	
		for i in range(n - k):
			diff = candies[(i + k) - 1] - candies[i] # since list is sorted, max is last element and min is first
			if min_diff == None or diff < min_diff: # mindiff == none because python treats 0 as false
				min_diff = diff
	
		return min_diff

#### What was the biggest change?

With these small changes, the 30 second script drops to a 10 second one. 
The most time saving operation? Removing `len(subgroup)` in our first 
step. If you're wondering why this has such a dramatic effect, I want you 
to think of what `len` has to do.

In order to tell how many items are in a list you need to count them. For 
a c programmer iterating over a linked list one might find code like this:

	int length = 0;
	for (Node * node = head; node != null; node = node->next)
		length++;
	
In python, you might find something similar:

	length = 0
	for x in list:
		length = length + 1
	
We of course already know that a single for loop will run in **O(N)** time, 
and even **O(N-k)** is still **O(N)** as far as Big O notation is concerned. But 
when you consider that the `len` function effectively adds a small loop
inside, then you can see that we're doing `k` small loops `N` times. In other 
words: **O(Nk)**

If you consider numbers, it's a decent different between 1000*3 and 1000, 
especially if you're taking sometime from 30 seconds down under 10. So really, 
the key to this optimization is the knowledge that `len` is going to add 
a very small loop to your code. And the intuition that slices act in a 
similar way, as they must iterate over a part of a loop to build a data 
structure. 

A slice from `i` to `i + k` is going to add another small loop
within our for loop: **O(Nk)** * 2, if you will. Granted the 2 is a constant 
and drops out. But it's still worth noting when you're in a performance 
contest, especially if you're dealing with actual imperical evidence of 
it slowing you down, and not just working within the theoretical Big O 
framework.

#### I'm a liar 😉

All of that said, I'd like to point out that the `len` function, despite 
what I just said, is [actually an O(1) operation]. But it's easier 
to reason and show a code example of how one would compute the length of 
a list then create a `slice` of a list. In this particular case, the real 
culprit of the O(Nk) time is the slice operation. As you can see in the 
[Time Complexity for lists], the slicing operation takes **O(k)** time 
for `k` elements. The reasons why this is the most expensive operation 
should be obvious to you after our discussion of `len`.
	
#### Did that answer your email Phelan? 

I hope that my musings and ramblings about lists and optimizations will 
help you in some way. The best advice I can give to anyone hoping to 
optimize their code is the following: _You need to understand what goes on 
under the hood before you can optimize_. It might be something obvious, a 
function you wrote that you knew was bad, or that a profiler has flagged 
for you. Or it might be something as simple as list slices, which 
you might forget actually has to do some work to compute a result! It's 
really all about understanding your code from the highest to the lowest 
levels, that's the only thing that can build a sense of intuition about 
where to look and what to change in order to optimize. 

Oh, and documentation about performance of common functions always helps!




	
[my friend Phelan]:https://github.com/the-hobbes
[Hacker Rank challenge about unfairness]:https://www.hackerrank.com/challenges/angry-children
[already optimized]:https://github.com/the-hobbes/misc/commit/30180c42fbef4fbd4673dcdd530696682c86052f
[slice]:http://www.dotnetperls.com/slice
[actually an O(1) operation]:https://wiki.python.org/moin/TimeComplexity
[Time Complexity for lists]:https://wiki.python.org/moin/TimeComplexity