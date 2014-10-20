### Teaching and Learning Through Games

At work recently I've had the task of mentoring a young student. This
involves teaching them how to program, how to approach problems related
to code, and how to help them improve themselves.

One of the biggest hurdles for students in learning is finding something
that engages them and challenges them without being absolutely over their
heads. Since I'm teaching this student C++, the level of detail they have
to learn in order to create even a simple program is far greater than if
I were teaching them something like python.

The other day, while thinking about what would be taught to my apprentice
I hit on the idea that I should use the same game which I learned while I
was their age. Which is a simplified game of [Nim], called the [21 game].
Up until this point the student had only been going over tutorials from 
[cplusplus.com]; which, while informative, aren't the most engaging.

So I coded up a quick game of Nim in about 5 minutes to share:

<script src="https://gist.github.com/EJEHardenberg/6da876d965bc57a33cbc.js"></script>

This was a simple game, which would work provided that the user entered
valid inputs. [We all know that's not going to happen and we must be defensive about our code].
So my lesson to the student today was built up of the following:

- Show them the game played correctly
- Show them how bad inputs affect the current program
- Nudge them in the right direction about how to approach 1 of the issues
- Answer any questions they had while they implemented solutions to the problems
- Repeat from step 2 until the program is defensive
- Add in new features, like a computer player, scoreboard, or playing the game 
  more than once

This lesson definitely engaged the student a lot more than sitting and 
reading tutorials all morning. Over the course of 3 hours I saw the proficiency
and understanding of the code increase. It was very rewarding. The student is
still new to programming, so best practices weren't really being followed here,
there was a `goto` to restart the game, there were redundant statements, and 
nothing was in functions. 

But, it was built up piecemeal, expanded on for each new feature, and it worked.
What's most important is that this was an encouraging lesson and engaging one to
the student, and it was easy to tell that they were enjoying this far more than
reading the tutorials from before.

I encourage you to take the little bit of code at the top and make your
own version of the game before looking at my implementation below that 
was created as I sat next to the student. Teaching is an amazingly rewarding
experience and really helps to ground your knowledge, it is one of the best
ways to learn and to refresh your own foundations. Highly recommend it.

<script src="https://gist.github.com/EJEHardenberg/c97d64f01eb7b29256eb.js"></script>

[We all know that's not going to happen and we must be defensive about our code]:http://en.wikipedia.org/wiki/Defensive_programming
[cplusplus.com]:http://www.cplusplus.com/
[Nim]:http://en.wikipedia.org/wiki/Nim
[21 game]:http://en.wikipedia.org/wiki/Nim#The_21_game
