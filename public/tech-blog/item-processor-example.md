###ItemProcessorListener Example, Spring Batch

For a recent work project I've been up to my ears in [Spring Batch], and besides
documentation, when I am thrown into a new project I tend to use [good examples]
of people using the library to supplement my learning. So when we decided that we
needed finer grain tracking of each item being processed, I went in search of
examples of item procesor listeners. 

The number one hit on google for spring batch listeners examples was [mykongs]
excellent example. The problem of course, is that him and everyone else I came
accross were _never_ using the ItemProcessListener. The closest thing to an 
example I could find was [this stackoverflow question].

The [ItemProcessListener] allows you to hook into the 3 core methods of the item
workflow. You can hook into it before the item is processed, after, and when the
processor throws an error. Throwing an error while you're in one of the three
listener methods will result in a failed step, so be care to check your exceptions!

The three methods you can use are intuitively named:

- afterProcess
- beforeProcess(T item)`
- onProcessError

One of the things you need to watch out for is that if your processor can return
null (i.e. you are filtering items out), then the `afterProcess/onProcessError` 
will also recieve the null object. Just one of those things to be aware of.

To create an item processor you need to implement the `ItemProcessListener<T,S>` interface:

	package com.example;

	public class MyExampleProcessorListener implements ItemProcessListener<Baz, Boz>{
		@Override
		public void beforeProcess(Baz baz){
			if(baz == null){
				//...
			}
			//...
		}

		@Override
		public void afterProcess(Baz baz, Boz boz){
			//..
		}

		@Override
		public void onProcessError(Baz baz, Exception e){
			//..
		}
	}

And in your configuration you need to have your step configured with your listener
specified in the configuration of your step:


	<bean id="exampleListener" class="com.example.MyExampleProcessorListener"  scope="step"/>

	<batch:job id="example" job-repository="jobRepository">
		<batch:step id="exampleStep">
			<batch:tasklet transaction-manager="transactionManager">
				<batch:chunk reader="" processor="" writer="" commit-interval="" />
			</batch:tasklet>
			<batch:listeners>
				<batch:listener ref="exampleListener" />
			</batch:listeners>
		</batch:step>
	</batch:job>

One of the things that tripped me up for a little bit was that the `listeners` 
tag in your XML setup **must** be within the step and not inside the tasklet.
Placing the listeners inside your chunk, tasklet, or anywhere else strange 
will result in the code simply not executing. One of the useful things that 
I walked away from that silly encounter was that XSD files and [xmllint] can be
very helpful when you're troubleshooting your xml configuration files.


[Spring Batch]:http://projects.spring.io/spring-batch/
[good examples]://www.mkyong.com/tutorials/spring-batch-tutorial/
[mykongs]://www.mkyong.com/spring-batch/spring-batch-listeners-example/
[this stackoverflow question]:http://stackoverflow.com/questions/18417753/implementing-itemprocesslistener-for-a-chain-of-itemprocessors
[ItemProcessListener]:http://docs.spring.io/spring-batch/trunk/apidocs/org/springframework/batch/core/ItemProcessListener.html
[xmllint]:http://xmlsoft.org/xmllint.html