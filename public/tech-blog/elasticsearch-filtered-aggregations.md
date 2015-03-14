### Narrow down options with Elastic Search

We've often seen web pages that offer an advance search feature. In a good one 
we'll see that as we select types of content, other criteria will fade out or 
fade in as neccesary. For example consider the following: 

Nancy logs on to awesome-articles.com <sup>[*](#footnote-1)</sup> and starts looking 
for an article how to fix her car. The search box has a few criteria: 

1. How many wheels does the vehicle have
2. What make is the vehicle
3. What model is the vehicle

After typing in 4 to the search box, all the pictures of motorcycles and such 
disappears from the listed articles. After entering "toyota" into the make 
field the list of models is restricted to toyota specific models. As she 
fills out additional fields so she can get her hands greasy, the results get 
more and more narrow until she finally finds the article she needs. 

This type of thing can be done pretty easily in elasticsearch using `query` 
and `aggregations`. These are both documented on [Elastic Search's webpage] 
and I suggest reading through the documentation to learn what's fully possible. 
Still, here's the general gist of what you need to do to support this as far as 
elastic search queries go:

	POST /yourindex/yourtype/_search
	{
	  "query": {
	    "bool": {
	      "must": [
	        {
	          "term": {
	            "wheels": {
	              "value": 4
	            }
	          }
	        },
	        {
	          "term": {
	            "make": {
	              "value": "toyota"
	            }
	          }
	        }
	      ]
	    }
	  }, 
	  "aggs": {
	    "models_available": {
	      "terms": {
	        "field": "model",
	        "size": 20
	      }
	    },
	    "someotherfieldthathastodowithcars_available": {
	      "terms": {
	        "field": "someotherfieldthathastodowithcar",
	        "size": 20
	      }
	    }
	  }
	}
 
First up, the `query` section specifies that this query should be restricted to 
items whose _wheels_ and _make_ match 4 and toyota. Additional queries could be 
used here, such as [match] if you wanted to widen the search. But for our car 
example described, we want to narrow down what's left for the other categories. 

What is left will be returned in the aggregations for `models_available` and 
`someotherfieldthathastodowithcars_available`. We'll get back 20 terms at most 
and we can then use those terms in a type-ahead style lookup or a dropdown. 

The resulting JSON will be something like this to your queries:

	{
	   "took": 68,
	   "timed_out": false,
	   "_shards": {
	      "total": 1,
	      "successful": 1,
	      "failed": 0
	   },
	   "hits": {
	      "total": 3,
	      "max_score": 0,
	      "hits": [
	      	//... data
	      ]
	   },
	   "aggregations": {
	      "models_available": {
	         "doc_count_error_upper_bound": 0,
	         "sum_other_doc_count": 0,
	         "buckets": [
	            {
	               "key": "atoyotamodel",
	               "doc_count": 1
	            },
	            {
	               "key": "yet another toyata model",
	               "doc_count": 1
	            }
	         ]
	      },
	      "someotherfieldthathastodowithcars_available": {
	         "doc_count_error_upper_bound": 0,
	         "sum_other_doc_count": 0,
	         "buckets": [
	            {
	               "key": "some",
	               "doc_count": 2
	            },
	            {
	               "key": "stuff",
	               "doc_count": 1
	            },
	            {
	               "key": "andyeah",
	               "doc_count": 1
	            }
	         ]
	      }
	   }
	}

So parsing this out with javascript is pretty easily done

	for( agg in a.aggregations ) { 
		var aggObject = a.aggregations[agg]; 
		for( idx in aggObject.buckets ) {
			var key = aggObject.buckets[idx].key
			// do something with the key, perhaps
			// add it to a list keyed by the agg index (the _available key)
		}
	}

If you take these pieces and combine them you can create a powerful and useful 
tool to allow users to look through and find your content. After all, that's 
what elastic search is all about! 

<small id="footnote-1">* I don't actually know if this is a website or not, but 
roll with it for the example</small>

[Elastic Search's webpage]:http://elastic.co/guide/en/elasticsearch/reference/master/search-aggregations-bucket-terms-aggregation.html
[match]:http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
