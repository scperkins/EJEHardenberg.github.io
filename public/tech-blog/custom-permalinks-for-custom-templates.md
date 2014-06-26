### Custom Permalinks for WordPress Custom Template Page or Custom Tables

I've blogged [before] about custom routing in WordPress, but today I faced a more
practical problem. Let's say you've create a page template and are displaying
some information on it based on the query parameters. For example:

`http://www.example.com/?page_id=47&recipe_id=1231`

And you've created a custom table for your recipes (though in this case they would
fit in as a post type, but for the sake of example bare with me). Say you've done
something like this:

	global $wpdb;
	if ( ! empty($wpdb->charset) )
		$charset_collate = "DEFAULT CHARACTER SET $wpdb->charset";
	if ( ! empty($wpdb->collate) )
		$charset_collate .= " COLLATE $wpdb->collate";
	
	$schema = "CREATE TABLE {$wpdb->prefix}recipes(
			ID bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
			slug varchar(255) NOT NULL,
			description TEXT
			) $charset_collate;";
	require_once( ABSPATH . 'wp-admin/includes/upgrade.php' );
	dbDelta( $schema );

And you've gone through all the effort to display the description and a bunch of
other information linked from other tables, but now you're stuck with URLs that 
look like the above, and you've decided they're ugly and you'd rather have a nice
structure like this:

`http://www.example.com/recipes/real-cool-recipe`

Where the `real-cool-recipe` is the slug of the recipe. Believe it or not, this
is actually pretty simple to do with WordPress permalinks! Though there is a very
dasterdly gotcha here:

**If another post is set to the same thing as your permalink's structure, you'll get
an endless redirect** 

More on that in a moment, here's how to do it:


functions.php
	
	add_action( 'init', 'vanity_setup' );
	function vanity_setup(){
		$pageId = 47; //pull this from the page with the recipes template
    	add_rewrite_rule(
	        'recipes/(([^/]+))?',
        	'index.php?page_id='.$pageId.'&recipe_id=$matches[1]',
        	'top'
    	);
	}

	add_filter( 'query_vars', 'vanity_vars' );
	function vanity_vars( $query_vars ){
	    $query_vars[] = 'recipe_id'; //dont forget this!
	    return $query_vars;
	}
 
	add_action('pre_get_posts', 'vanity_permalink', 10, 3);
 
	function vanity_permalink($query) {

		if(if_on_recipe_index_page()){
			return;
		}
    	if( isset($query->query_vars['recipe_id']) 
    		&& !empty($query->query_vars['recipe_id']) 
    		&& !is_numeric($query->query_vars['recipe_id']) 
    		&& isset($query->query_vars['page_id']) ){

    			switch ($query->query_vars['page_id']) {
    				case 47:
    					$query->query_vars['recipe_id'] = Recipe::getIdBySlug($query->query_vars['recipe_id']); 
    					if(empty($query->query_vars['recipe_id'])){
    						//404...
    					}
    				break;
    			default:
	    			break;
    			}    	
    	}
	}

Alright, so let's examine the code! 
First off, we create our rewrite rule, this **must** be setup in or before the init 
action. Because we know our page id then you can go ahead and use your knowledge
to set which page we'll actually load (since we need it's template). Next, we
create the redirect rule `'index.php?page_id='.$pageId.'&recipe_id=$matches[1]'`
which tells wordpress to treat it like we're getting the page_id and the recipe_id
as query parameters. This is why we filter the query_vars and add the variable.
**The variable will not be availabled from `$_GET` becuase WordPress will filter it out.**

Next, we do 'the magic' as it were. Mapping our slug to the id field in the `pre_get_posts`
action. Note the call to `if_on_recipe_index_page()` is to prevent redirects. If
you had another page whose name was `recipes`, and then set the permalink structure
to display single recipes in `recipes/slug` and didn't do this, WordPress would 
keep jumping between them until your browser got tired.

All the checks in the condition before the switch statement is because we only
want to filter the calls we want to know about. Then the switch statement is useful
for if you need multiple structures like this and want to handle them in one routing 
function.

Note that once you use something like this you will have to save your permalinks
everytime you make a change to the rule in the `add_rewrite_rule`.


Hope this helps someone!


[before]:http://www.ethanjoachimeldridge.info/tech-blog/shortcodes-routing-wordpress