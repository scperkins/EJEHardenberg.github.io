###Form with name="name" causes 404 in WordPress

While I haven't tracked down the source of the problem within WordPress itself,
I was having some trouble with a form on a custom template on a WordPress site.

I had made my form, was hitting submit then promptly seeing a 404 page. 

Confusing? I'll say, especially considering the form was submitting to itself. 
So I took a look at my code, commented out the redirects I had, through `error_log`
around a little trying to track down where the execution broke. Nothing. No err's,
no warnings.

So I did what any developer does, I googled a few keywords checking for 404 errors
on submitting a form, and then eventually ended up on [this support forum] where
member [ianstapleton] noted that changing the input name caused the form submission 
to work again. 

It's a bit of a strange fix, but it makes sense when you consider the code inside of 
Wordpress Core. Here's the snippet that is causing the slightly unexpected behavior:

```
wp-includes/query.php (WordPress Version 3.7.1)
2337		if ( '' != $q['name'] ) {
2338			$q['name'] = sanitize_title_for_query( $q['name'] );
2339			$where .= " AND $wpdb->posts.post_name = '" . $q['name'] . "'";
2340		} elseif ( '' != $q['pagename'] ) {
2341			if ( isset($this->queried_object_id) ) {
```

The `$q` variable is the query variables which are retrieved like this:
```
2142		$q = &$this->query_vars;
2143
2144		// Fill again in case pre_get_posts unset some vars.
2145		$q = $this->fill_query_vars($q);
```

In other words, the `$_POST` and `$_GET` variables seem to be merged into a single
`query_vars` propertie and then used from there. `wp_parse_args` is used during
part of the merging (from a brief look into the `fill_query_vars` function) and
so we end up looking for a post with the name of whatever we submitted in the form.
Which is, not what we wanted to do. You could use it to create a custom search
form for looking for exact matches on post names, but that'd be a little silly. 

Regardless, I wonder if this is the intended behavior of WordPress or just a result
of lots of code making the assumptions that no user will ever try to use

```
<input type="text" name="name" />
```

[this support forum]:http://wordpress.org/support/topic/posting-form-to-custom-template-results-in-404
[ianstapleton]:http://wordpress.org/support/profile/ianstapleton