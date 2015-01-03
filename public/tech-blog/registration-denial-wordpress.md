### Denying known spam accounts on WordPress 

Let's say you've made a WordPress site, you're pretty happy about it, and you've 
decided you want to talk to your readership via comments. But you don't want any 
anonymous comments or to use disqus, and instead you want people to register on 
your website. So you enable registration for everyone and write your posts. 

Fast forward a few months and suddenly you've got 10,000 users registered but 
half of them are random spam accounts. You start looking through and notice 
that a lot of the domain names for the websites end in russian domains, or have 
domain names outside of what you're used to seeing, such as .ru, .li, .website.

This isn't that hard to do with the wordpress filter `registration_errors` and 
an implementation is rather simple:

	function my_simple_domain_check($errors, $sanitized_user_login, $user_email) {
		//fill out this list with any problem domains
		$spamdomains = array(
			'.li',
			'.website',
			'.ru'
		);
		$ip = isset($_SERVER['X-Forwarded-For']) ? $_SERVER['X-Forwarded-For'] : (isset($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR']);
		foreach ($spamdomains as $domain) {
			if ( strpos($user_email, $domain) !== false ) {
				$errors->add( 'spam_error', __('<strong>ERROR</strong>: Registration halted, please contact support.','mydomain') );
				error_log('SPAMALERT: [email:' . $user_email . ', IP Address: ' .  $ip .']');
			} else { 
				error_log('NEWUSER: [email:' . $user_email . ', IP Address: ' .  $ip .']');
			}
		}

	    return $errors;
	}

	add_filter('registration_errors', 'my_simple_domain_check', 10, 3);

Simply add problematic domain names into the `$spamdomains` variable and users 
will not be able to register from those names. If you notice that a lot of those 
spam users are coming from a single IP address, than you can use something like 
[iptables] to drop their packets. The `X-Forwarded-For` header is checked first 
because if you're behind a load balancer this is where the real ip address will be 
(the `remote_addr` will be the ip of the load balancer and you don't want to ban 
that!)

I might create a simple plugin that creates a friendlier interface to non-programmers 
that logs the information to a database instead of the error log. Having a relatively 
clean error log can be important. After all, exceptions should be exceptional.

[iptables]:http://www.cyberciti.biz/faq/linux-howto-check-ip-blocked-against-iptables/