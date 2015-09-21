### New Relic XML and Scala Objects

Recently, I've been getting into monitoring applications. There's a lot of 
different options out there to choose from. But I've recently got into 
[New Relic]. New Relic is useful for monitoring and profiling because if 
you choose to use the [XML Instrumentation] you _don't have to change the 
source code of your program._ Which is a really useful thing. 

However, the instrumentation takes place _in java_, which means that if 
your scala code compiles down to a different name than you expect, it can 
be troublesome to inspect it. Thankfully, we have tools for this. Namely, 
the tool [javap], which we can run on `.class` files and see the generated
methods and names. 

So first off, here's an example of a singleton object in scala. This code is 
roughly based on [the guardian's].

	package com.example 

	import java.io.{ByteArrayInputStream, ByteArrayOutputStream}

	import org.im4java.core.{Info, ConvertCmd, IMOperation}
	import org.im4java.process.{Pipe,ProcessStarter}

	object Im4Java {
	  /** Run an im4java operation on an array of byts from an Image 
	   *
	   * @param operation The IMOperation to run
	   * @param imageBytes An array of bytes containing image data
	   * @return The resulting bytes of the image output from running the command
	   */
	  def apply(operation: IMOperation)(imageBytes: Array[Byte]): Array[Byte] = {
	    val cmd = new ConvertCmd(false)

	    val pipeIn = new Pipe(new ByteArrayInputStream(imageBytes), null)
	    cmd.setInputProvider(pipeIn)

	    val baos = new ByteArrayOutputStream
	    val s2b = new Pipe(null, baos)
	    cmd.setOutputConsumer(s2b)    

	    blocking {
	      cmd.run(operation)
	    }    

	    baos.flush()    
	    baos.toByteArray
	  }

	  /** Resize an image to have a certain width, maintaining proportions 
	   *
	   * @param width The width to resize an image to
	   * @param imageBytes An array of bytes containing image data
	   * @return A Future[Array[Byte]] containing the resized images data
	   */
	  def resizeBufferedImage(width: Int)(imageBytes: Array[Byte]) = future {
	    val operation = new IMOperation

	    operation.addImage("-")
	    operation.resize(width)
	    operation.sharpen(1.0)
	    operation.quality(0)
	    operation.addImage("jpg:-")

	    apply(operation)(imageBytes)
	  }
	}

When this code compiles, we actually end up with _a lot_ of little classes:

	$ ls com/example/
	Im4Java$$anonfun$apply$1.class
	Im4Java$$anonfun$resizeBufferedImage$1.class
	Im4Java$.class
	Im4Java.class

One for each function actually. This is likely due to the currying (or at 
least that's my intuitive guess, correct me if I'm wrong dear reader). You
can inspect these on the command line with `javap`:

	javap com/example/Im4Java\$.class 
	Compiled from "Im4Java.scala"
	public final class com.example.Im4Java$ {
	  public static final com.example.Im4Java$ MODULE$;
	  public static {};
	  public byte[] apply(org.im4java.core.IMOperation, byte[]);
	  public scala.concurrent.Future<byte[]> resizeBufferedImage(int, byte[]);
	}


So, when you're doing a [pointcut] for New Relic's instrumentation, you need
to choose the right class to instrument. Which in this case, is `Im4Java$` 
(I found this through trial and error):

	<pointcut excludeFromTransactionTrace="false" ignoreTransaction="false" transactionType="web">
		<className includeSubclasses="true">com.example.Im4Java$</className>
		<method>
			<name>apply</name>
		</method>
		<method>
			<name>resizeBufferedImage</name>
		</method>
	</pointcut>

Doing something like the above in your xml extension will produce something 
like the following log output if you've done it right:


	Sep 21, 2015 13:31:13 -0400 [12585 35] com.newrelic FINE: create Transaction com.newrelic.agent.Transaction@2cd14001
	Sep 21, 2015 13:31:13 -0400 [12585 35] com.newrelic FINE: created com.newrelic.agent.TransactionActivity@0 for com.newrelic.agent.Transaction@2cd14001
	Sep 21, 2015 13:31:13 -0400 [12585 39] com.newrelic FINEST: Instrumentation skipped by 'no source' rule: sun/reflect/GeneratedConstructorAccessor33
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINER: Matched method apply(Lorg/im4java/core/IMOperation;[B)[B for instrumentation.
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINER: Matched method resizeBufferedImage(I[B)Lscala/concurrent/Future; for instrumentation.
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic DEBUG: Instrumenting class com/example/Im4Java$
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINER: Traced com/example/Im4Java$ methods [apply(Lorg/im4java/core/IMOperation;[B)[B, resizeBufferedImage(I[B)Lscala/concurrent/Future;]
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINE: Instrumented com.example.Im4Java$.apply(Lorg/im4java/core/IMOperation;[B)[B, [LocalCustomXml], [libim-extension]
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINE: Instrumented com.example.Im4Java$.resizeBufferedImage(I[B)Lscala/concurrent/Future;, [LocalCustomXml], [libim-extension]
	Sep 21, 2015 13:31:14 -0400 [12585 39] com.newrelic FINER: Final transformation of class com/example/Im4Java$

Some notes about creating new relic extensions:

1. They go into an `extensions` directory within the unzipped newrelic package 
for your respective language
2. The name of the file and the name attribute of the `extension` tag should be the same
3. Setting the transactionType of the pointcut to web will allow it to show up in the overview page, rather than have to drill down to transaction.


[New Relic]:http://newrelic.com/
[XML Instrumentation]:https://docs.newrelic.com/docs/agents/java-agent/frameworks/scala-installation-java
[javap]:http://www.scala-lang.org/api/2.11.1/scala-compiler/index.html#scala.tools.util.Javap
[the guardian's]:https://github.com/guardian/frontend/blob/4bca926fa2affa2e62966e3f97ed854ad299aac8/png-resizer/app/lib/Im4Java.scala
[pointcut]:http://blog.espenberntsen.net/tag/pointcut/