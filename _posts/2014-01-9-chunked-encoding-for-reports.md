---
title: Using Chunked Encoding for Reporting in Wordpress
layout: post
---

Note: Before you use the TL;DR due be sure it's appropriate to do so, see [here](http://wordpress.stackexchange.com/questions/20192/wp-function-filter-for-modifying-http-headers)

###The TL;DR;

    add_action('template_redirect', 'add_chunked_encoding_for_reports_page_bc_load_speed');
    function add_chunked_encoding_for_reports_page_bc_load_speed(){
        header("Transfer-encoding: chunked");    
    }

###The Explanation

So, for work I've written a number of adminstrative pages for a client that 
involved some kind of reporting. Most of the time, the bulk of the computation 
could be done on the database side, which is where it should be (almost always).
But because the lists sometimes would show large amounts of tabular data the page can take a while to load. 

So, to make things appear to load a bit better, I decided to switch the transfer
type to chunked instead of the default. Now, I was doing all this reporting only
on the admin area, so I actually used the `init` hook and checked `is_admin` in
my call to the action. In addition, I did **not** place the code into `functions.php`
like many people do. But rather it is within my own plugin's page. So only when users go to the reports page is the action enabled and the content served up as
chunked.
