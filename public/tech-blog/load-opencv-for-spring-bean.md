### Use OpenCV for Spring Bean XML Configuration

Today I ran into an infuriating issue that lasted for several hours. Here's the 
stack trace I was given when trying to run `mvn tomcat:run`:

	Caused by: org.springframework.beans.BeanInstantiationException: Could not instantiate bean class [org.opencv.ml.CvSVM]: Constructor threw exception; nested exception is java.lang.UnsatisfiedLinkError: org.opencv.ml.CvSVM.CvSVM_0()J
	    	at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:162)
	    	at org.springframework.beans.factory.support.SimpleInstantiationStrategy.instantiate(SimpleInstantiationStrategy.java:76)
	    	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.instantiateBean(AbstractAutowireCapableBeanFactory.java:990)
	    	... 56 more
    Caused by: java.lang.UnsatisfiedLinkError: org.opencv.ml.CvSVM.CvSVM_0()J
    	at org.opencv.ml.CvSVM.CvSVM_0(Native Method)
    	at org.opencv.ml.CvSVM.<init>(CvSVM.java:63)
    	at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
    	at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:57)
    	at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
    	at java.lang.reflect.Constructor.newInstance(Constructor.java:534)
    	at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:147)
    	... 58 more

Linker errors are normally because you failed to call `System.loadLibrary` and
then your JNI fails since it knows about your classes via the Jar wrappers around
the native code (and will compile) but at runtime you're out of luck. My problem 
was doubly more confusing because at runtime my [OpenCV] code worked fine, but 
stopped when I tried to put one of the classes into an XML bean. Then the error 
above happened.

So how do you fix it? Simple, you need to call `System.loadLibrary` ... **from 
the XML**. But how to do this obvious thing? For classes that depend on native
libraries the general pattern you do is the following:

	import some.native.library.*;
	public class SomethingThatNeedsNativeSupport {
    	static {
        	System.loadLibrary(NATIVE_LIBRARY_NAME);
    	}
    }

But for XML configuration? It's surprisingly difficult to google for, and it wasn't
until I talked to one of my coworkers about the issue that he told me the obvious
answer: The [depends-on property] pointed at a loader class. 

I had already thought to box the classes that were failing as beans in my own 
wrapper implementations since I could run the classes fine in the actual Java code
(luckily I didn't have [this guys issue]), but a loader class was way easier, and
now I can use XML to configure the OpenCV classes. Here's the code:

	//OpenCVLoader.java
	package info.ethanjoachimeldridge.cv;
	import org.opencv.core.*;

	public class OpenCVLoader {
 		static {
	        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
	    }
	}

Throw that into your package and then do something like the following in your XML:

	<bean id="cvLibLoader" class="info.ethanjoachimeldridge.cv.OpenCVLoader" />
	<bean id="svm" class="org.opencv.ml.CvSVM" depends-on="cvLibLoader"/>

The `depends-on` property of the bean will force that bean to be initialized before
the other, and therefore the library will be loaded when Spring gets around to 
loading the class.

Hope this helps anyone else out there who's using [Spring Batch] and [OpenCV] together.

[this guys issue]:http://stackoverflow.com/questions/3155589/java-lang-unsatisfiedlinkerror-under-tomcat
[OpenCV]:http://docs.opencv.org/
[depends-on property]:http://docs.spring.io/spring/docs/2.5.3/reference/beans.html
[Spring Batch]:http://projects.spring.io/spring-batch/