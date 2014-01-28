Well, I've been using [my program] to keep track of my time on a few projects 
and have made a few additions since the alpha release I talked about in my last
post. Just taking a quick look through my gitk for the repository and I'm seeing
a few noticable improvements:

- Pause command
- Fix to finished tasks
- Info file fix
- Delete command
- Proper task name resolution for view -a 
- A fix for a warning for ARMx86 architectures.

The pause command is essentially the same as the start command with the switch 
flag, except that you don't have to be switching to a task ( you can actually 
take a break from tasks! ). It's quickly becoming a fast favorite of mine.

The delete command was born out of my scrolling through the view -a output and
wanting to have a better way of deleting the tasks then manually removing the
sequence and information files from the .tc directory. I use it everynow and 
then, although out of habit I write rm sometimes, it's starting to make me think
I should shortcut rm to be delete. 

The fixes in the list are minor things, the task state being wrong when finishing
a task (it would show in progress until I fixed it), mind you it was only wrong 
during the finishing of the task's final output, not when it was viewed later. 

The info file fix was something a bit silly where I forgot to not write out the
taskInfo field of the struct that I was using to store the name of the info file
itself. This caused the info file to end up with a bunch of filepaths at the end
of the file. Not particularly harmful to the file, and useful sometimes, but not
desired behavior. 

The task resolution name fix is to handle task names with spaces in them to be 
shown correctly when using the view --all command. Before I was only reading out
one string from the line to use as the name, and this was causing some minor
annoyances when I was trying to delete a task and wasn't using it's full name. 
 
Finally, I was surprised all the warning flags and pedantry passed in my makefile
didn't catch this, but within the delete command I do ask for user confirmation. 
Out of sleep-deprived silliness I used char instead of int for the result of 
getc(stdin) and anyone whose read [K &amp; R] will tell you that EOF is an int
because it simply has to be. So I wasn't actually able to check the value of the
user input again the EOF properly. Luckily, [my friend] happened to be compiling
timecatcher on his raspberry pi and caught the warning for me. 

That last warning catch is only on the develop branch of the repository as I 
didn't have time to do a hotfix or release yet. But it will be included in my
next release, which should have a feature I've been wanting to implement:

<pre>
	tcatch resume
</pre>

In the same way that pause pauses the current task, I want to be able to resume
the most recent task that was paused or finished. Why? Because I start up a task
and work on it, then get distracted for a moment and pause my task, but then 
after responding to an email or whatever got in the way of coding, I start up 
the task I was previously working on. In fact, I do this so often I think a 
command would be a great idea for this. 

The other feature I want to implement is using gnuplot and the sequence files of
all tasks to plot some typeo of time spent on different tasks over the course
of some time, and see how much time you spent on each one. These types of small
statistics are useful for someone like me who wants to know what bogs them down
the most so they can focus on getting better at it. 

The only other addition to timecatcher is that my other friend [Garth] has 
expressed some interest in collaborating in it with me, so who knows maybe it 
won't just be my name on the commit log soon! 

[Garth]:https://github.com/gfritz/
[my friend]:https://github.com/primehunter326
[K &amp; R]:http://en.wikipedia.org/wiki/The_C_Programming_Language
[my program]:https://github.com/EJEHardenberg/timecatcher