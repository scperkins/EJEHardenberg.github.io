###Adding Actions to the WordPress User Lists

Today I was working on extending the functionality of an ecommerce site
plugin I've been working on. Primarily, I decided it would be a great 
idea if an Admin could easily jump to view a users purchases. 

Where to do this? The WordPress Users list of course! It's the most likely
place an admin would goto checkout their customers. So I jumped in and 
looked around and ended up finding the action and filter: `manage_users_custom_column`,
and `manage_users_columns`. As well as [a whole], [bunch], [of great links] detailing how
to add your own columns to the user list screen. 

Those were all great, and I had even used one already to add in a column for store
credit. But, I wanted to modify the existing columns. Trying out `unset`ing a default
field and adding in my own, then trying to throw in my custom code didn't work. 

Investigating WordPress core I soon found out why. It took a few `grep`s and `ctrl+
shift+F`'s but I found the file `wp-admin/includes/list-table.php` at last and after
investigating that code found the more useful and informative file `wp-admin/includes/class-wp-users-list-table.php`
 where hidden away inside the function `single_row` was an easy to see reason why
 the custom filtering on the default fields hadn't worked. They're hardcoded for
 all the columns besides the first one. 

 The first column happened to echo out the contents of the `$edit` variable, which
 is created from a list of actions that can be done for that row. And here I found
 the filter: `user_row_actions` which passes 2 arguments, the actions array and the
 user object. This is exactly what I needed as after that, it was easy enough to 
 simply do the following:

```
    add_filter('user_row_actions', 'custom_user_actions',10, 2);
    function custom_user_actions($actions, $user_object ){
    	$actions['see purchases'] = "<a class='submitdelete' href='" . admin_url( 'admin.php?page=user-purchases&user='.$user_object->ID) . "'>" . __( 'Purchases' ) . "</a>";
    	return $actions;
    }
```

And then my purchases link appeared on the WP Users list page in the admin view. Perfect!

I hope that this helps someone else out there who needs to add actions to the user 
list view. 

[a whole]:http://wordpress.stackexchange.com/questions/3233/showing-users-post-counts-by-custom-post-type-in-the-admins-user-list
[bunch]:http://themeforest.net/forums/thread/help-with-manage_users_columns-in-wordpress/50906
[of great links]:http://pippinsplugins.com/add-user-id-column-to-the-wordpress-users-table/