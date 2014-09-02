###Easy scale generation with Less CSS

Something I found myself doing for [a side project] is creating [Likert Scales]. 
One day this past week I got to thinking, Hey, I could use different colors on 
this thing to make it not look so bland, and to give users a visual cue as well.

<img style="padding-left: 25%" src="/images/tech-blog/likert-scale.png" width="476px" height="56px" />

####The Problem

The traditional way of doing this in pure CSS might look something like this:

    .strongly-disagree{
    	background-color: red;
    }
    .disagree{
    	background-color: orange;
    }
    /* ... */

Or if you like pseudo selectors and don't want to use classes, something like this:

	/* Provided all labels are wrapped in the same div, with radio buttons nested */
    label:nth-child(1){
    	background-color: red;
    }
    label:nth-child(2){
    	background-color: orange;
    }
    /* ... */

To me. this is not very attractive. After all, you're repeating the same selector, 
over and over again just because the background color changes. There must be a better
way to do it with all of our new and fancy modern tools right? Right.

####The Code

By using [LESS] we can make it a lot easier to achieve the same affect without cluttering
our markup with a lot of unneccesary classes. Granted we do need to do a little bit
of trickery with LESS mixins. Here's the code:

	@from: 1;
	@to: 5;
	@scaleColors: red, orange, yellow, lime, green;
	.scale(@idx) when(@idx =< @to){
		&:nth-child(@{idx}){
			@col: extract(@scaleColors, @idx);
			background-color: @col;
			color: black;
			font-weight: bold;
			&:hover	{
				background-color: white;
			}
			&:active{
				/* This causes a quick flash when the radio button is clicked */
				background-color: blue;
			}
		}
		.scale(@idx + 1);
	}

####Explanation

This is a recursive [Mixin], calling itself until we go from `@from` to `@to`. In
the case of our 5 point scale, this is obviously 5. We have a list of colors we
can want to use, and then are using the `extract` function of LESS to grab the
colors out of our list for usage as the local variable `@col`. You'll notice at
the bottom of our Mixin that we call it again `.scale(@idx + 1)` with an increment
to the passed in `idx` value. This causes our function to count up for each element.

You could use [a loop] as well to get the same effect if you dislike the recursion.
The rest of the code is regular CSS styling each element. Besides using a list of 
colors, you can also use a single base color and then lighten/darken it like so:

	@scaleColor: #000;
	@from: 1;
	@to: 5;
	.scale(@idx) when(@idx =< @to){
		&:nth-child(@{idx}){
			background-color: lighten(@scaleColor, @idx*20);
			color: black;
			font-weight: bold;
			&:hover{
				background-color: darken(lighten(@scaleColor, @idx*20), 30);
				color: white;
			}
		}
		.scale(@idx + 1);
	}

Which uses the same technique to loop through children, but instead of a list of 
colors we use `lighten` and `darken` to automatically make a bunch of shades of a base
background color. You might need to modify it for your own uses though, changing
the base color can change whether you need to use the lightening features of LESS
or the darkening. Also the code above could be cleaned up by placing `lighten(...)` into a local 
variable, then darkening that only in the `:hover` selector.

Another Mixin that I find rather useful is my `.Transition` mixin shown below:

	.Transition{
		-o-transition:.5s;
	    -ms-transition:.5s;
	    -moz-transition:.5s;
	    -webkit-transition:.5s;
	    transition:.5s;
	}

which I include on the scale elements so that background shift is a bit cleaner
looking. I hope this helps anyone out there looking to do something similar.


[a side project]:https://github.com/EJEHardenberg/whoseopinion.com
[Likert Scales]:http://en.wikipedia.org/wiki/Likert_scale
[LESS]:http://lesscss.org/
[Mixin]:http://lesscss.org/features/#mixins-feature
[a loop]:http://lesscss.org/features/#loops-feature