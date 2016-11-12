### ElasticSearch, Regular Expressions, and Text Anchors

#### A bit of background

The other day I was helping a co-worker write some tests for one of our 
systems that uses ElasticSearch. The use case wasn't that crazy: we had 
a text field that we were enabling search for, and as part of our spec we 
decided that if a user typed some text than that'd become a regular 
match search, but we also wanted to enable them to use `*` to indicate a 
wildcard. 

One of the first tests we had written was just checking that we respected 
our ordering parameters, so the test was something like this:

	filter fixture's from test with field T starting with "t"
	do a search for all content with field T starting with "t*"
	verify list of results match fixtures and is ordered right

And this appeared to work fine for us, at least until my co-worker started 
writing a test for the functionality I mentioned above and his test string 
was something like `"my really cool text"`. All of a sudden the test above 
started failing. 

The reason? Because `T` was a simple text field, and if you pay attention 
to the [documentation on Regexp Query's]

>Lucene’s patterns are always anchored. The pattern provided must match the entire string.

If you don't understand why this sentence relates to my co-workers dummy 
text string, then you've forgotten one simple thing: _elastic search 
breaks up a text string into tokens_. It's these tokens which are being 
matched against, so when the documentation says that the patterns are 
anchored, that means that in the string `"my really cool text"`, the 
_token_ of `text` will match `t.*`. We're not considering the whole string 
of text as one piece, but as multiple tokens. So what if we wanted to?

#### Anchoring a search to an entire field

While our use case didn't call for this (we like tokens and so do our 
users), it got me thinking. If you wanted to support searching against 
the entire field, with an anchor at the beginning of the text, how would 
you do that, while still allowing regular match queries to use the tokens 
we know and love?

You could use a prefix query and nix the `*`. Or:

The answer is actually pretty simple. Use [copy_to]! If you're not aware, 
`copy_to` allows us to copy the value of one field to an indexed version 
that can have other analyzers applied to it. This means that we can keep 
an exact match copy and a version of a string broken up into tokens. By 
doing this, we're able to have a regular expression consider the entire 
field as the string it will apply an anchored search to. 

In case that doesn't all click. Here's an example of a [sense] session I 
did to demonstrate the technique to my co-worker:

First, we make an index with a mapping defining a copied field:

	PUT example_copy
	{
		"mappings": {
			"example" : {
				"properties": {
					"original" : {
						"type": "string",
						"copy_to": "copied"
					},
					"copied" : {
						"type": "string",
						"index": "not_analyzed"    
					}
				}
			}
		}
	}

Next, we index some data:

	POST /example_copy/example
	{
		"original" : "hello there friend"
	}

Note: If you take a look at the documents returned by searches, you'll 
see that only the `original` field is returned, the `copied` field is 
not part of the source document, and that's the way it should be.

A regular expression search against our tokenized field:

	POST /example_copy/_search 
	{
	    "query": {
	        "regexp" : {
	            "original" : {
	                "value" : "t.*"
	            }
	        }
	    }
	} 

The above will return the document we indexed because the `t` matches 
the token `there`. But, if we search on our `copied` field with the same
search:

	POST /example_copy/_search 
	{
	    "query": {
	        "regexp" : {
	            "copied" : {
	                "value" : "t.*"
	            }
	        }
	    }
	}

You'll get 0 results. That's because the text `"hello there friend"` 
doesn't begin with `t` like the search value requires. But if you were
to search for an `h.*` like so:

	POST /example_copy/_search 
	{
	    "query": {
	        "regexp" : {
	            "copied" : {
	                "value" : "h.*"
	            }
	        }
	    }
	}

Then you'd get back your document, this is because `h` is the start of 
the string `"hello there friend"`. 

#### Note about version

ElasticSearch _just_ came out with version 5.0.0, and if you're paying 
attention you might have noticed I'm pointing to the 1.3 version 
documentation, and that's because legacy code will do that to ya! That
said, `regexp` queries are still part of the DSL in 5.0.0, as is the 
`copy_to` functionality. So you can do the above in the latest version 
if you need to! 

[documentation on Regexp Query's]:https://www.elastic.co/guide/en/elasticsearch/reference/1.3/query-dsl-regexp-query.html#_standard_operators
[copy_to]:https://www.elastic.co/guide/en/elasticsearch/reference/1.3/mapping-core-types.html#copy-to
[sense]:https://www.elastic.co/blog/found-sense-a-cool-json-aware-interface-to-elasticsearch