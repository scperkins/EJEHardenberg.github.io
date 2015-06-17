### Basic Manipulation of XML with PHP 

Even though I've been on a [Scala kick recently], PHP is still the language 
I'd consider the most common on the web. As such, we often need to dive into 
legacy systems or perform things in the language no matter what our opinion 
of its [insanity]. Considering that PHP and XML go hand in hand on occasion, 
(basing this on the current [32,265 results on StackOverflow]) I figure'd I'd 
write up a quick post about some common use cases for the two.

#### The DOM

The first thing to understand about XML and PHP is that, like everything in PHP, 
there's a [module dedicated to it]. And it's worth it to quickly peruse the 
available functions for the `DOMDocument`, `DOMNode`, and `DOMElement` classes. 
The other thing worth looking into is [XPATH]. 

I won't go into this too much, but using XPath is probably the best way to 
manipulate a subset of a Tag if you need to. For example, if you wanted to 
add an attribute of "jackass" to only Tags that had an attribute of `partner="X223"` 
for your internal record keeping. More on this later. 

For all the examples, assume you have the following available to you:
	
	<?php
	$xml = <<<XML
	<?xml version="1.0" encoding="utf-8"?>
	<Things>
		<Thing name="one">
			<Color>Red</Color>
		</Thing>
		<Thing name="two">
			<Color>Blue</Color>
		</Thing>
	</Things>
	XML;

	$dom = new DomDocument();
	$dom->loadXml($xml);
    $dom->formatOutput = true;
    $document->preserveWhiteSpace = false;
    $xpath = new DOMXPath($dom);

In case you're curious, the format `<<<XML ... XML;` is called a [HEREDOC]. 
Which is pretty handy for declaring large strings. Read the linked documentation 
if you're curious about how to use it.

#### Set the Value of an XML Node with PHP 

Let's say we get orders from on high that from henceforth, all Things must be 
Yellow. How do we set the value of the `Color` tag in our XML?

	function setAllTagToValue($dom, $tagName, $value) {
		$tags = $dom->getElementsByTagName($tagName);
		foreach ($tags as $domElement) {
			$domElement->nodeValue = "";
			$domElement->appendChild($dom->createTextNode($value));
		}
	}

	setAllTagToValue($dom, "Color", "Yellow");

Will do the trick. The `getElementsByTagName` returns a `DOMNodeList`. Which 
implements [Traversable] and can be iterated over by `foreach`. You might be 
wondering why we set `nodeValue` to an empty string? Consider what would 
happen if we didn't! If we didn't reset the node Value, we'd end up with this 
as our XML:

	<?xml version="1.0" encoding="utf-8"?>
	<Things>
		<Thing name="one">
			<Color>RedYellow</Color>
		</Thing>
		<Thing name="two">
			<Color>BlueYellow</Color>
		</Thing>
	</Things>

Notice that without reseting the text, all we do is add text to the text node 
inside the tag. We can use this knowledge to create a method:

	function appendStringToTagValue($dom, $tagName, $value) {
		$tags = $dom->getElementsByTagName($tagName);
		foreach ($tags as $domElement) {
			$domElement->appendChild($dom->createTextNode($value));
		}
	}

	appendStringToTagValue($dom, "Color", " is this thing's color");

What about the converse of this? Prepending text to a node? Pretty similar: 

	function prependStringToTagValue($dom, $tagName, $value) {
		$tags = $dom->getElementsByTagName($tagName);
		foreach ($tags as $domElement) {
			$oldValue = $domElement->nodeValue;
			$domElement->nodeValue = "";
			$domElement->appendChild($dom->createTextNode($value . $oldValue));
		}
	}

	prependStringToTagValue($dom, "Color", "My ");

Which is just the two previous functions combined in a different order. Running 
the above would result in the following xml:

	<?xml version="1.0" encoding="utf-8"?>
	<Things>
		<Thing name="one">
			<Color>My Yellow is this thing's color</Color>
		</Thing>
		<Thing name="two">
			<Color>My Yellow is this thing's color</Color>
		</Thing>
	</Things>

#### Add a Node to an XML Tag

Ok, so we can now adjust the value of a text node, what if we want to _add_ a 
node? We want our `Thing`s to also contain their disposition. We can use the 
`$dom->createElement` and `$domElement-appendChild` to accomplish this:

	function addElementToTag($dom, $tagName, $elementName, $elementText) {
		$tags = $dom->getElementsByTagName($tagName);
		foreach ($tags as $domElement) {
			$newElement = $dom->createElement($elementName);
			$newElement->appendChild($dom->createTextNode($elementText));
			$domElement->appendChild($newElement);
		}
	}

You might think to yourself, why not just create the element once and then add 
it to the appropriate tags? Surely that would be better? The results of code 
like this would not be what you'd expect:

	// Incorrect! Will only add to the LAST of $tagName
	function addElementToTag($dom, $tagName, $elementName, $elementText) {
		$newElement = $dom->createElement($elementName);
		$newElement->appendChild($dom->createTextNode($elementText));
		$tags = $dom->getElementsByTagName($tagName);
		foreach ($tags as $domElement) {	
			$domElement->appendChild($newElement);
		}
	}

	addElementToTag($dom, "Thing", "Disposition", "Mischievious");

Results in:

	<?xml version="1.0" encoding="utf-8"?>
	<Things>
		<Thing name="one">
			<Color>Red</Color>
		</Thing>
		<Thing name="two">
			<Color>Blue</Color>
			<Disposition>Mischievious</Disposition>
		</Thing>
	</Things>

Which is a good reminder that manipulating the dom is a side-effecting 
operation, and moving pieces around can be done pretty easily. Which leads 
to our next step. 

#### How do I remove a Tag from an XML Node? 

Ok, so maybe it's not quiet the right seque, but we're getting there. Here's 
how to remove a Tag from XML:

	function removeTag($dom, $tagName) {
    	$tagsToRemove = $dom->getElementsByTagName($tagName);
    	$elementsToRemove = array();
    	foreach ($tagsToRemove as $domElement) {
      		$elementsToRemove[] = $domElement;
    	}
    	foreach ($elementsToRemove as $domElement) {
       		$domElement->parentNode->removeChild($domElement);
    	}
  	}

Wait what? Why do we have to iterate twice? The answer to this lies in the 
implementation of `DomNodeList` itself. You can see in the [source], that the 
node list is essentially a linked list. As such, the `->next`, if we were to 
do something like this: 

	function removeTagWRONG($dom, $tagName) {
		$tagsToRemove = $dom->getElementsByTagName($tagName);
		foreach ($tagsToRemove as $domElement) {
			$domElement->parentNode->removeChild($domElement);
		}
	}

Gets screwed up a bit since we're effecting the list we're iterating over. If 
you attempt to use the `removeTagWRONG` function, the XML will only remove the 
first element matching the TagName. Consider that every operation on the dom 
has a side effect on the underlying document. If we remove an element from a 
list, then we have effected the underlying list structure underneath. So it's 
not that surprising that we stop iterating, since after we've removed that 
element there is no `next` pointer underneath. 

But I don't want to iterate twice you say! Alright, we can do this if we go over 
the list _backwards_. Weird? Yeah, but hey, it's PHP, try not to think about it 
to hard. 

	function removeTag($dom, $tagName) {
		$tagsToRemove = $dom->getElementsByTagName($tagName);
		$i = $tagsToRemove->length -1;
		while($i >= 0) {
			$domElement = $tagsToRemove->item($i);
			$domElement->parentNode->removeChild($domElement);
			$i--;
		}
	}

This is using an alternate method of accessing the nodes we haven't seen yet. 
The use of `->item(index)` on the `DomNodeList` itself. It's good to note that 
you can use this at anytime if you can't use `foreach` for whatever reason. 

#### Adding an Element before another Element 

Let's say that we want to add a new `Thing` to our XML file. But orders from 
on high has declared we need to put this new `Thing` after the one which has 
an attribute of `name="two"`. How do we do this? 

Firstly, we'll be needing to pull out _only_ the `Thing` with the specified 
attribute. Secondly, we'll have have to insert a new node before it. For this 
we can use xpath and the `insertBefore` method on the [DomNode] class. 

Using our previous declared `$xpath` variable, we can perform Queries on the 
dom and retrieve [DomNodeList] results we can use. Here's an example: 

	$xPathResult = $xpath->query('/Things/Thing[@name="two"]');
	// xPathResult contains a node list of length 1, with a single DomElement (Thing) 

For a good list of xPath examples, check out the [wikipedia] page. The above 
example queries for a Thing, which is a descendent of a Things tag, and has 
an attribute of `name="two"`. Note that `@` is what specifies we're looking 
for an attribute. 

With this, we have the first half of our puzzle. Now how do we use it to insert 
an element before the other? 

	// Make the new element
	newElement = $dom->createElement("Thing");
	$newElement->appendChild($dom->createElement("Color", "Orange"));
	$thingTwo = $results->item(0);
	thingTwo->parentNode->insertBefore($newElement,thingTwo);

What if we were inserting the same element before more than one node though? 

	$results = $xpath->query('/Things/Thing');
	foreach($results as $result) {
		$newElement = $dom->createElement("Thing");
		$newElement->appendChild($dom->createElement("Color", "Orange"));
        $result->parentNode->insertBefore($newElement,$result);
	}

Take care to create the new element within the iteration, or you'll be faced 
with the same issue as before. Having only a single element appear before the 
last matching element. 

#### Set attributes on Tags

Our regular XML string had a few attributes, so how do we set this? We have 
two options. Use `createAttribute` from the `DomDocument` class, or use 
`setAttribute` method on the `DomElement`. We'll use the second since it's 
more obvious in how it works: 

	$dom = new DomDocument("1.0","utf-8"); //new document using UTF-8 encoding, and version 1 of xml.
	$elem = $dom->createElement("Something");
	$dom->appendChild($elem);
	$elem->setAttribute("name","value");
	print $dom->saveXml();
	// Output: 
	// <?xml version="1.0" encoding="utf-8"?>
	// <Something name="value"/>

Pretty simple right? There's really not much to say about this besides that it 
will escape the value for you. So calling `setAttribute("name","&val");` will 
result in a node with `name="&amp;val"`. 

#### Put it all together

Using these basics we can do some pretty simple XML manipulation. Let's go 
ahead and construct our string Xml using the functions we've defined: 

	<?php
	$dom = new DomDocument("1.0", "utf-8");
	$thingsElem = $dom->createElement('Things'); //need a root to play with
	$dom->appendChild($thingsElem);
	$dom->formatOutput = true;
	$xpath = new DOMXPath($dom);
	addElementToTag($dom, "Things", "Thing", null);
	addElementToTag($dom, "Things", "Thing", null);
	addElementToTag($dom, "Thing", "Color", "Blue");
	addElementToTag($dom, "Thing", "Disposition", "Mischievious");

	// Set the first Thing's color to red
	$firstInList = $xpath->query("(/Things/Thing/Color)[1]"); //select first Color Node, note xpath indexes start at 1, not 0!
	foreach($firstInList as $domElement) {
		$domElement->nodeValue = "";
		$domElement->appendChild($dom->createTextNode("Red"));
	}

	// Set the attribute for each Thing's Name!
	$thingNames = array("one", "two");
	$things = $xpath->query("/Things/Thing");
	$i = 0;
	foreach($things as $thing) {
		$thing->setAttribute("name", $thingNames[$i] );
		$i++;
	}

	print $dom->saveXml();
	/* 
	  Results in the following xml: 
	  <?xml version="1.0" encoding="utf-8"?>
	  <Things>
		<Thing name="one"><Color>Red</Color><Disposition>Mischievious</Disposition></Thing>
	    <Thing name="two"><Color>Blue</Color><Disposition>Mischievious</Disposition></Thing>
	  </Things>
	*/


Hopefully you've found this somewhat useful, and can approach XML in PHP
with a little knowledge about how to do the basics. Good luck! 


[Scala kick recently]:/tech-blog/reverse-routing-package-controller
[insanity]:/tech-blog/dear-god-why
[32,265 results on StackOverflow]:http://stackoverflow.com/search?q=%5Bxml%5D+php
[module dedicated to it]:http://php.net/manual/en/class.domdocument.php
[XPATH]:http://php.net/manual/en/class.domxpath.php
[HEREDOC]:https://php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc
[Traversable]:http://php.net/manual/en/class.traversable.php
[source]:http://lxr.php.net/xref/PHP_5_3/ext/dom/nodelist.c#105
[DomNode]:http://php.net/manual/en/class.domnode.php
[DomNodeList]:http://php.net/manual/en/class.domnodelist.php
[wikipedia]:https://en.wikipedia.org/wiki/XPath#Syntax_and_semantics_.28XPath_1.0.29
