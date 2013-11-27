---
title: Git Crash Course
layout: post
---

Ran into a funny thing today. If you're performing a wordpress search
with WP_Query, and you're using the post__in parameter to specify an
array of ID's to retrieve and your array is _empty_ then you end up with
the post__in field ignore entirely and the other parameters taking
precedence. 

This is rather strange, as I'd expect it to show 0 posts since no ID's
would match an empty list. 

Specifically, my arguments to WP_Query were along these lines:

```
    $query_args = array( 	 
    'post_type' => 'redacted',
    'post_status' => 'publish',
    'posts_per_page' => $limit,
    'paged' => $page,
    'post__in' => $ids,
    'meta_key' => '_expiration_date', 
    'meta_value' => time(), 
    'meta_compare' => '>=',
    'ignore_sticky_posts'= > true
    );
```

If my `ids` array was empty, then I'd just get **everything** back.
Which isn't what I wanted at all, so to fix the problem I just
initialized the array with -1 and it all worked the way I expected it
to. 

Well, weirder things have happend. I wonder if this is a WordPress bug
or intentional?


