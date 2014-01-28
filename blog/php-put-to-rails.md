

Working on a project for work involving a Rails server and a WordPress
plugin I came accross the need to perform a PUT to Rails. Simple right?

PHP supports cURL and I can easily use that to go ahead and perform a
put. Right.

So instead of running off to documentation, I immediately googled for
"php curl put" and quickly found a way to do it. Better yet I found
[this link]. Which seemed great. Until I tried it of course. Nothings
that easy.

    Started PUT "/redacted/redacted" for 127.0.0.1 at 2013-09-12 12:00:55 -0400
    Error occurred while parsing request parameters.
    Contents:
    
    
    
    MultiJson::LoadError (795: unexpected token at '-truncated--'):
      path/ruby/1.9.1/gems/json-1.8.0/lib/json/common.rb:155:in `parse'
      path/ruby/1.9.1/gems/json-1.8.0/lib/json/common.rb:155:in `parse'
      path/ruby/1.9.1/gems/multi_json-1.7.9/lib/multi_json/adapters/json_common.rb:16:in `load'
      path/ruby/1.9.1/gems/multi_json-1.7.9/lib/multi_json/adapter.rb:19:in `load'
      path/ruby/1.9.1/gems/multi_json-1.7.9/lib/multi_json.rb:118:in `load'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/json/decoding.rb:15:in `decode'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/params_parser.rb:47:in `parse_formatted_parameters'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/params_parser.rb:17:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/flash.rb:242:in `call'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/session/abstract/id.rb:210:in `context'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/session/abstract/id.rb:205:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/cookies.rb:341:in `call'
      path/ruby/1.9.1/gems/activerecord-3.2.14/lib/active_record/query_cache.rb:64:in `call'
      path/ruby/1.9.1/gems/activerecord-3.2.14/lib/active_record/connection_adapters/abstract/connection_pool.rb:479:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/callbacks.rb:28:in `block in call'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/callbacks.rb:405:in `_run__4211912891873951081__call__1368528194962300028__callbacks'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/callbacks.rb:405:in `__run_callback'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/callbacks.rb:385:in `_run_call_callbacks'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/callbacks.rb:81:in `run_callbacks'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/callbacks.rb:27:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/reloader.rb:65:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/remote_ip.rb:31:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/debug_exceptions.rb:16:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/show_exceptions.rb:56:in `call'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/rack/logger.rb:32:in `call_app'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/rack/logger.rb:16:in `block in call'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/tagged_logging.rb:22:in `tagged'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/rack/logger.rb:16:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/request_id.rb:22:in `call'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/methodoverride.rb:21:in `call'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/runtime.rb:17:in `call'
      path/ruby/1.9.1/gems/activesupport-3.2.14/lib/active_support/cache/strategy/local_cache.rb:72:in `call'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/lock.rb:15:in `call'
      path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/static.rb:63:in `call'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/engine.rb:484:in `call'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/application.rb:231:in `call'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/content_length.rb:14:in `call'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/rack/log_tailer.rb:17:in `call'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/connection.rb:81:in `block in pre_process'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/connection.rb:79:in `catch'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/connection.rb:79:in `pre_process'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/connection.rb:54:in `process'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/connection.rb:39:in `receive_data'
      path/ruby/1.9.1/gems/eventmachine-1.0.3/lib/eventmachine.rb:187:in `run_machine'
      path/ruby/1.9.1/gems/eventmachine-1.0.3/lib/eventmachine.rb:187:in `run'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/backends/base.rb:63:in `start'
      path/ruby/1.9.1/gems/thin-1.5.1/lib/thin/server.rb:159:in `start'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/handler/thin.rb:13:in `run'
      path/ruby/1.9.1/gems/rack-1.4.5/lib/rack/server.rb:268:in `start'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/commands/server.rb:70:in `start'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/commands.rb:55:in `block in <top (required)>'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/commands.rb:50:in `tap'
      path/ruby/1.9.1/gems/railties-3.2.14/lib/rails/commands.rb:50:in `<top (required)>'
      script/rails:6:in `require'
      script/rails:6:in `<main>'
    
    
      Rendered path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/templates/rescues/_trace.erb (1.1ms)
      Rendered path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/templates/rescues/_request_and_response.erb (0.9ms)
      Rendered path/ruby/1.9.1/gems/actionpack-3.2.14/lib/action_dispatch/middleware/templates/rescues/diagnostics.erb within rescues/layout (8.4ms)
    
Ok so what's wrong? 

I hunted a bit more and found the ACTUAL support for PUT in the cURL php
library. you can only PUT a _file_. 

Well damn. Alright we can deal with that: So then I wrote up a quick
little hack to send my request along:

    function _putHack($url,$data){
    	$tmpFileFD = tmpfile();
    	$filesize = fwrite($tmpFileFD, json_encode($data));
    	fseek($tmpFileFD,0);
    	$ch = curl_init($url);
    	$headers = array(
        				'Accept: application/json',
        				'Content-Type: application/json',
    					);
    	curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    	curl_setopt($ch, CURLOPT_PUT, TRUE);
    	curl_setopt($ch, CURLOPT_INFILE, $tmpFileFD);
    	curl_setopt($ch, CURLOPT_INFILESIZE, $filesize);
    	$res = curl_exec($ch);
    	if ($res === false) {
    	    $info = curl_getinfo($ch);
    	    curl_close($ch);
    	    die('error occured during curl exec. Additional info: ' . var_export($info));
    	}
    	curl_close($ch);
    	fclose($tmpFileFD);
    	return $res;
    }


And just like that I have a working PUT request from PHP to rails. It
costs me a temporary file, but hey if that's what I have to do to get my
REST semantics correct then by Turing that's what I'll do. 

Something nice to know is that the PHP tmpfile() function call creates a
temporary file (obviously) but when you call fclose on it to clean up,
the file is automatically deleted, which is great because otherwise your
system would get clogged really fast. 

It seems kind of silly if you ask me that PUT requires a file to work
properly. I mean, it make's sense given the PUT request history as a
user of "putting" a file onto a server. But if I'm updating a resource
that exists in a database or something (which I would say is a more
common use of it) then it makes more sense to not use a file and allow
for arbitrary strings. After all, the command line cURL PUT request
takes a string and accomplished what I'd like to do. 

I hope this little hack helps someone out there whose getting PHP to
talk to Rails like I am.


[this link]:http://support.qualityunit.com/061754-How-to-make-REST-calls-in-PHP

