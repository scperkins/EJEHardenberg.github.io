### Thoughts on Github Awesome Autocomplete

It's not every day a [really awesome developer] reaches out and contacts 
you. But that happened today, so I was pretty excited to give feedback about the 
[Github Awesome Autocomplete] extension and figured the best way to do 
so would be to write up a quick post about it.

#### What is it?

GAA is an extension that acts on [github] and [github.algolia.com] that adds a fancy search box onto github.

<img src="https://github.com/algolia/github-awesome-autocomplete/raw/master/capture.gif" title="Source: https://github.com/algolia/github-awesome-autocomplete" width="800px"/>
<small>[Source]:https://github.com/algolia/github-awesome-autocomplete</small>

So the question is how does Algolia's search box compare to github's built in one? Funny enough, a few weeks ago my co-worker asked me if I knew any good open source projects that he could hack on. I searched github and tried to find something for him

<img src="/images/tech-blog/opensourcesearch.png" />

I didn't find much when I did my original search, but what about using the 
enhanced search offered by the Algolia plugin?

<img src="/images/tech-blog/opensourcesearch2.png" />

This is much more interesting, I can instantly a community of users who 
are likely to be contributing to interesting projects, a user's profile 
which might have some good links, and of course the 3 repositories of 
Bitcoin, search engines, and something from Medium.

#### Usefulness? 

I'd score this one pretty high if you like to browse github looking for 
projects to contribute to. Or if you're looking for tutorials this is a 
good way to search for them. Honestly, type in a language, tutorial and 
poof!

<img src="/images/tech-blog/scala.png">

The other thing I could see this as being useful for, is if you need to 
search your own repositories often for information. For example, when 
doing the [green up] application, I often consulted my [api documentation]
while developing to conform my work to the spec. While eventually my 
browser just autocompleted, this tool would have saved me the effort of 
clicking through my profile and repositories tab; so I can see it being
a productivity boost to companies that have a lot of internal documentation
in markdown on github or who check on issues often.

#### Overall?

Overall, I really like this extension, enhancing the search on github is 
pretty cool, and the value something like this has to companie's that 
use github for their day to day work is pretty obvious. The ability to 
have the extension search private repositories (after oauth) is also 
handy for anyone hoping to keep their project secret while improving their
productivity. 

I'd recommend you check it out and see if you can find any interesting 
projects on github to contribute to or use in your next project!

#### Trying to nitpick

I felt that I needed to come up with something bad to say about the extension,
but the [FAQ] hits on any major concerns I can think of from someone using it,
anything about public users or repo's not being found to where your private
repository information is sent to. Thinking about privacy brings me to 
thinking about the "right to be forgot", in which perhaps one should be 
able to request their repositories (even their public ones) be searchable. 
Though since Algolia pulls the information from the [github archives] that
burden falls more on github than Algolia.

Looking through the issue's page on the github, I can see one [enhancement]
that I think would be helpful as it'd make it really easy to quickly find 
a file within the repository and check it out (such as when browsing source
code that you haven't downloaded to grep). Speaking of issues, according 
to the current documentation in the README, after connecting with oauth, 
the extension is supposed to add instant search and suggestion to the 
issues page as well. I didn't see this happen, but there's also no 
documentation on what I was supposed to see either. So this area could be 
[improved by Algolia]  (at least with documentation) to make their extension 
even better. 

Even with that one caveat, this is still a great extension as I've mentioned 
and I look forward to seeing what new versions bring!


[Source]:https://github.com/algolia/github-awesome-autocomplete
[github]:https://github.com
[github.algolia.com]:https://github.algolia.com/
[really awesome developer]:http://sylvain.utard.info/
[Github Awesome Autocomplete]:https://github.com/algolia/github-awesome-autocomplete
[green up]:http://www.ethanjoachimeldridge.info/tech-blog/green-up-vt-app
[api documentation]:https://github.com/EdgeCaseBerg/GreenUp/tree/master/api
[FAQ]:https://github.com/algolia/github-awesome-autocomplete#faq
[github archives]:http://www.githubarchive.org/
[enhancement]:https://github.com/algolia/github-awesome-autocomplete/issues/8
[improved by Algolia]:https://github.com/algolia/github-awesome-autocomplete/issues/16