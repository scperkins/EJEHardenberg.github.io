### Concurrent Java - Partial Processing of Web Services

In a web world, we often pull data from multiple services and other API
servers. So you might pull a list of accounts from billing's services, 
then check in with what the accountant's are saying, and have some type 
of reporting system that is verifying all the information and finding 
discrepencies. 

However, since the information is pulled from tons of different potential 
sources, it makes sense to try to be fault tolerant. For example, if the 
billing department has maintenance on their services one day and every
thing is running slowly, but the reporting system is fine with being out 
of date or having stale data for a short time, then we can implement some
solutions.

Let's say we have a list of products that belong to an account. Let's also
suppose we have an HTTP service that returns more information per account 
that we need. So we have a simple client connecting to retrieve the data 
based on the list of id's. Something like this:

1. System reporting on account A
2. System retrieves list of product id's for account A
3. System grabs each product from the service for further processing

While one might simply implement a service that returns all products (the 
full object) for a single account. Another system might not do such things
because it uses large memory cache's for each product resource and is 
designed to take that type of load. Regardless of reason, let's assume 
the latter is our system.

A simple method of doing this somewhat efficiently is to process each 
request asynchronously in it's own thread. For that, we can use [ExecutorService] 
to write some simple and readable code.

    private final ExecutorService pool = Executors.newFixedThreadPool(numPools);
    List<Future<Product>> futures = new ArrayList<Future<Product>>();
        
    //for each product id
    futures.add(pool.submit(new Callable<Product>() {
    	@Override
    	public Product call() {
    		//http request to get product object
    	}
    }));
    
    List<Product> products = ...
    for(Future<Product> product : futures) {
    	products.add(product.get());
    }

    //carry on and error handling as neccesary

Assuming that the service returning the products is fast,this code will work just 
fine. But what if it get's slow? Well, we could add timeout's to the call to 
`product.get()` like this:

	List<Product> products = ...
	for(Future<Product> product : futures) {
		product.add(product.get(4L, TimeUnit.SECONDS));
	}

Once we do this, we'll only wait 4 seconds for each product, but that means that 
for a list of products of size N, we might end up waiting N*4 seconds. This could 
get large fast and cause problems for the user looking at these reports. So the 
alternative is that instead of having each HTTP Request thread have it's own timeout, 
we can place a timeout on the entire pool by using the function `invokeAll`.

This is pretty easy to do, simply create a list of `Callable` instead of `Future`s 
and pass them to `invokeAll` with a timeout specified. Here's a complete code 
example:

	import java.util.List;
	import java.util.Collection;
	import java.util.ArrayList;
	import java.util.concurrent.*;
	import java.lang.InterruptedException;
	import java.util.concurrent.ExecutionException;
	import java.util.concurrent.CancellationException;

	public class TimeoutExample {
		private final ExecutorService pool = Executors.newFixedThreadPool(50);

		private long getThingThatTakesAWhile(long milliSecs) throws InterruptedException{
			System.out.println("Starting task that will take  " + milliSecs + " milliSecs!");
			Thread.sleep(milliSecs);
			System.out.println("Done task that took " + milliSecs + " milliSecs!");
			return milliSecs;
		}

		public void doStuff() {
			int sizeOfList = 10; 
			Collection<Callable<Long>> tasks = new ArrayList<Callable<Long>>(sizeOfList);

			for (int i =0; i < sizeOfList ; i++) {
				final int j = i;
				tasks.add(new Callable<Long>() {
					@Override
					public Long call() throws InterruptedException{
						return getThingThatTakesAWhile(300L*j);
					}
				});
			}

			List<Long> valuesReturned = new ArrayList<Long>(sizeOfList);
			try {
				List<Future<Long>> returnedResults = pool.invokeAll(tasks, 2L, TimeUnit.SECONDS);
				pool.shutdown(); // do this here otherwise you will block and wait for others
				for (final Future res : returnedResults) {
					final Long cal = (Long)res.get(0,TimeUnit.SECONDS);
					valuesReturned.add(cal);
				}
			/* The next three exceptions won't happen in our example ... */
			} catch (InterruptedException ie) {
				System.out.println("InterruptedException!");
			} catch (ExecutionException ee) {
				System.out.println("ExecutionException!");
			} catch (TimeoutException te) {
				System.out.println("TimeoutException!");
			/* But this one will because we did cancel some callable's */
			} catch (CancellationException ce) {
				System.out.println("CancellationException!");
			}

			/* Will print out the first 7 since they were within the time limit */
			int got = 0;
			for (final long res : valuesReturned) {
				System.out.println(res);
				got++;
			}

			System.out.println("Retrieved [" + valuesReturned.size() +  "/" + sizeOfList + "]");
		}

		public static void main(String[] args) {
			TimeoutExample ct = new TimeoutExample();
			ct.doStuff();
		}

	}

When you run this, you'll get an output somewhat like this:

	Starting task that will take  0 milliSecs!
	Starting task that will take  1500 milliSecs!
	Starting task that will take  900 milliSecs!
	Starting task that will take  600 milliSecs!
	Starting task that will take  300 milliSecs!
	Starting task that will take  1200 milliSecs!
	Done task that took 0 milliSecs!
	Starting task that will take  2100 milliSecs!
	Starting task that will take  1800 milliSecs!
	Starting task that will take  2700 milliSecs!
	Starting task that will take  2400 milliSecs!
	Done task that took 300 milliSecs!
	Done task that took 600 milliSecs!
	Done task that took 900 milliSecs!
	Done task that took 1200 milliSecs!
	Done task that took 1500 milliSecs!
	Done task that took 1800 milliSecs!
	CancellationException!
	0
	300
	600
	900
	1200
	1500
	1800
	Retrieved [7/10]

As you can see, we hit the [CancellationException] when we tried to `get` one of 
the tasks that took longer than the `2L` timeout we set in the `invokeAll` call. 
Of course, this code works because we have an increasing number in order for each
of our sleeping threads called in that order. If we mixed it up though, such as 
doing something like this:

    import java.util.Random;
    Random rand = new Random();
	for (int i =0; i < sizeOfList ; i++) {
		final int j = i;
		final int randomNum = rand.nextInt((4000 - 0) + 1) + 0;
		tasks.add(new Callable<Long>() {
			@Override
			public Long call() throws InterruptedException{
				return getThingThatTakesAWhile(randomNum);
			}
		});
	}

Then we are not guaranteed to hit the canceled task last! In fact, if we were to 
only replace the relevant part with the above code, we might get an output like 
this from the program:

	Starting task that will take  2798 milliSecs!
	Starting task that will take  1408 milliSecs!
	Starting task that will take  80 milliSecs!
	Starting task that will take  1318 milliSecs!
	Starting task that will take  3343 milliSecs!
	Starting task that will take  660 milliSecs!
	Starting task that will take  3335 milliSecs!
	Starting task that will take  1115 milliSecs!
	Starting task that will take  539 milliSecs!
	Starting task that will take  310 milliSecs!
	Done task that took 80 milliSecs!
	Done task that took 310 milliSecs!
	Done task that took 539 milliSecs!
	Done task that took 660 milliSecs!
	Done task that took 1115 milliSecs!
	Done task that took 1318 milliSecs!
	Done task that took 1408 milliSecs!
	CancellationException!
	Retrieved [0/10]

Notice how we didn't get anything in our retrieved list even though we know some 
tasks were finished? We can get these if we check if a task was cancelled first:

	for (final Future res : returnedResults) {
		if (!res.isCancelled()) {
			final Long cal = (Long)res.get(0,TimeUnit.SECONDS);
			valuesReturned.add(cal);
		}
	}

Then the results of our program can come out like this: 

	Starting task that will take  2010 milliSecs!
	Starting task that will take  2886 milliSecs!
	Starting task that will take  2944 milliSecs!
	Starting task that will take  803 milliSecs!
	Starting task that will take  3830 milliSecs!
	Starting task that will take  512 milliSecs!
	Starting task that will take  3758 milliSecs!
	Starting task that will take  2943 milliSecs!
	Starting task that will take  936 milliSecs!
	Starting task that will take  3156 milliSecs!
	Done task that took 512 milliSecs!
	Done task that took 803 milliSecs!
	Done task that took 936 milliSecs!
	936
	512
	803
	Retrieved [3/10]

And now no matter what order the tasks start, we'll get back the ones that 
finish within the time limit. One of the key things to note here that may 
not be immediately obvious is the call to `pool.shutdown()`. This is **very** 
important. If you don't call `shutdown` then you might have tasks hanging out 
in the background taking up resources without doing anything useful. If you'd 
like your programs to be leak free, be sure to call shutdown if you use this 
technique! 

In our fictional scenario with products and accounts, we could use this number 
retrieved to let the user know that some data may not be correct, or log events 
that could notify us of slowness or issues in other services. 

[ExecutorService]:http://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ExecutorService.html
[CancellationException]:http://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CancellationException.html
