### Lost and Found Application

Last year I made a simple [gh-pages lost and found application] powered
by a google doc. It worked well and did the job but I decided to kick
some life into it again in order to try out [flakes] and to use my small
[PHP utility library] which has a stupid simple ORM. 

The lost and found software assumes nothing about the items you are
losing. In fact, without the sample data loaded in, it's entirely up to
you to create the event space, the feature types, and the features of
items that might be lost. The rational behind being that every event is
different and empowering the user to handle each seperately will make
for an easier searching experience later on. 

<img src="/images/tech-blog/lostfound-1.png">

As you can see above, the user isn't left on their own as the index page
is a simple guide on each of the different parts of the system. If
someone reads the page and then proceeds, they shouldn't (I believe)
have any trouble. 

The application runs off of the idea of _features_, AKA noticible things
about objects you might find. For example, color is a great feature
type. With the software you can quickly add that in, then create the
color's you'd expect and proceed to have a better method of search. If
you're at an convention of some kind and know the brand of certain
items, add that as a feature type! Have a large space? Use location as a
feature type and list the rooms for each feature. It's all customizable
by your event and space. 

Flakes provides a very clean and professional style to forms, tables,
and the page in general. The tables in the inventory management screen
are the default and do a great job of making the data easily readable
and clear. 

<img src="/images/tech-blog/lostfound-2.png">

The framework also provides a simple grid system that makes arranging
elements on the screen pretty easy, the best example of this is probably
the Manage Criteria page (pictured below). It's a simple layout, but
used again on the search screens to position whatever types of features
the user comes up in a clear manner. 

<img src="/images/tech-blog/lostfound-3.png">

The reporting page is based on the features and types you create.
Completely customized to whatever criteria has been made. For each event
space you create, you'll have a link in the sidebar to the reporting
page for it. Within the application there is a simple switch to shut off
the sidebar on the reporting page. This can work well for using a
computer as a kiosk (full screen the report item page). 

<img src="/images/tech-blog/lostfound-4.png">

I made this program working for a few minutes or sometimes an hour or so
over the past few weeks, you can find the repository on [github here] if
you'd like to try it out. You'll need a PHP and mySQL compatible web
server and a few minutes to set it up. If you'd like to add to it feel
free to send pull requests or make suggestions. 

[gh-pages lost and found application]:https://github.com/EdgeCaseBerg/col-con-lost-n-found/tree/gh-pages
[flakes]:http://getflakes.com/preview/dashboard.html
[PHP utility library]:https://github.com/EdgeCaseBerg/php-util
[github here]:https://github.com/EdgeCaseBerg/col-con-lost-n-found
