###College fried Chicken

I've recently picked up cooking, taking pictures of my food, and [SnapChat]ting 
my meals to all my friends. For the few that respond positively, I generally 
share the recipes with them via a painful exercise in thumb-fu on my tiny phones
keyboard. To say the least, writing out ingredient lists and instructions within 6 texts 
(my phone has a maximum of 960 characters for multi-part messages) is a pain. 

I had been playing around with [Harp] and was inspired to explore the idea of a Static
site with dynamic content. So after looking into HTML template's and decided on
using Handlebars, I started creating a simple site that loaded up a template with
an image in it. After a while, the idea to place my recipes onto the site to share
them with my friends occured to me.

It was very easy to implement. The whole thing probably only took a couple of hours
at most. To make generating the content easier, I created a form that created copyable JSON
data that should be sent along with an image to my email. Git savvy cooks could fork the project
and submit a pull request with a modification to the recipe.js file as well as an image. There's
no need to specify img/ in the Image url because the template I created includes the directory
by default. 

I showed it to my friend and she sent me a couple recipes and I added them to the site. Pretty
much anything goes with what kinds of recipes. I created a simple title search box that
helps filter out the content pretty easily. 

It was a fun project and I'll probably keep adding recipes to it as I cook more. You can check it out 
[here]

[SnapChat]:http://www.snapchat.com/
[Harp]:http://harpjs.com
[here]:http://ethanjoachimeldridge.info/cooking/
