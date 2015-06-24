### Could not instantiate SVGImageReader in Scrimage

Today I was testing out the scala library [scrimage]. I wrote a pretty 
simple sbt script:

_Main.scala_:

	package ee.test

	import java.io.File
	import com.sksamuel.scrimage._

	object Main {
		def main(args: Array[String]): Unit = {
		  val image = Image.fromFile(new File("./testimage.jpg"))

		  val scaled50 = TestOps.resize50(image)
		  val scaled300 = TestOps.resize300(image)
		  val crop = TestOps.crop(image, (420, 420), 500, 500)

		  scaled50.output(new File("./50.jpg"))
		  scaled300.output(new File("./300.jpg"))
		  crop.output(new File("./crop.jpg"))
		}
	}

_TestOps.scala_:

	package ee.test

	import com.sksamuel.scrimage._

	object TestOps {
		def resize50(image: Image) : Image = {
			image.fit(50,50)
		}

		def resize300(image: Image) : Image = {
			image.fit(300,300)
		}

		def crop(image: Image, center: (Int, Int), widthOfCrop: Int, heightOfCrop: Int) : Image = {
			/* trim left top right bottom */
			image.trim(
				center._1 - (widthOfCrop/2), 
				center._2 - (heightOfCrop/2), 
				image.width - (center._1 + widthOfCrop/2), 
				image.height - (center._2 + (heightOfCrop/2))
			)
		}
	}

And lastly, _build.sbt_

	name := "scrimage-test"

	version := "0.1"

	scalaVersion := "2.10.4"

	libraryDependencies += "com.sksamuel.scrimage" %% "scrimage-core" % "2.0.0"

	libraryDependencies += "com.sksamuel.scrimage" %% "scrimage-io" % "2.0.0"

I was testing out my script when all of a sudden a giant error message 
spewed itself across my console:

	Could not instantiate SVGImageReader (missing support classes).
	java.lang.NoClassDefFoundError: org/apache/batik/transcoder/TranscoderException
		at com.twelvemonkeys.imageio.plugins.svg.SVGImageReaderSpi.onRegistration(Unknown Source)
		at javax.imageio.spi.SubRegistry.registerServiceProvider(ServiceRegistry.java:715)
		at javax.imageio.spi.ServiceRegistry.registerServiceProvider(ServiceRegistry.java:302)
		at javax.imageio.spi.IIORegistry.registerApplicationClasspathSpis(IIORegistry.java:211)
		at javax.imageio.ImageIO.scanForPlugins(ImageIO.java:110)
		at com.sksamuel.scrimage.Image$.<init>(Image.scala:718)
		at com.sksamuel.scrimage.Image$.<clinit>(Image.scala)
		at ee.test.Main$.main(Main.scala:8)
		at ee.test.Main.main(Main.scala)
		at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
		at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:57)
		at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
		at java.lang.reflect.Method.invoke(Method.java:606)
		at sbt.Run.invokeMain(Run.scala:67)
		at sbt.Run.run0(Run.scala:61)
		at sbt.Run.sbt$Run$$execute$1(Run.scala:51)
		at sbt.Run$$anonfun$run$1.apply$mcV$sp(Run.scala:55)
		at sbt.Run$$anonfun$run$1.apply(Run.scala:55)
		at sbt.Run$$anonfun$run$1.apply(Run.scala:55)
		at sbt.Logger$$anon$4.apply(Logger.scala:85)
		at sbt.TrapExit$App.run(TrapExit.scala:248)
		at java.lang.Thread.run(Thread.java:745)
	Caused by: java.lang.ClassNotFoundException: org.apache.batik.transcoder.TranscoderException
		at java.net.URLClassLoader$1.run(URLClassLoader.java:366)
		at java.net.URLClassLoader$1.run(URLClassLoader.java:355)
		at java.security.AccessController.doPrivileged(Native Method)
		at java.net.URLClassLoader.findClass(URLClassLoader.java:354)
		at java.lang.ClassLoader.loadClass(ClassLoader.java:425)
		at java.lang.ClassLoader.loadClass(ClassLoader.java:358)
		... 22 more
	[success] Total time: 3 s, completed Jun 24, 2015 4:03:35 PM

While it didn't actually cause any errors in my script and the image 
operations were successful, I don't like seeing warnings like this when 
I'm working. So I started looking around. After a little bit of looking 
I found one of the forementioned errors in [this issue], but the answer 
there didn't make much sense to me. I didn't _have_ any SVG plugins 
attempting to register to TwelveMonkeys that I knew of. My class path 
didn't show much to help from first glance: 

	ls ~/.ivy2/cache/com.twelvemonkeys.imageio/imageio
	imageio/          imageio-iff/      imageio-pict/     imageio-thumbsdb/
	imageio-batik/    imageio-jpeg/     imageio-pnm/      imageio-tiff/
	imageio-bmp/      imageio-metadata/ imageio-psd/      
	imageio-core/     imageio-pcx/      imageio-sgi/      
	imageio-icns/     imageio-pdf/      imageio-tga/    

Looking at the root cause, `the org.apache.batik.transcoder.TranscoderException` 
I looked around some more on the internet and found this [useful list of common
exceptions from batik]. A quick glance at the mvn repositorie's and I updated 
my build file:

	name := "scrimage-test"

	version := "0.1"

	scalaVersion := "2.10.5"

	libraryDependencies += "com.sksamuel.scrimage" %% "scrimage-core" % "2.0.0"

	libraryDependencies += "com.sksamuel.scrimage" %% "scrimage-io" % "2.0.0"

	libraryDependencies += "org.apache.xmlgraphics" % "batik-codec" % "1.7"

Then the error message disappeared. Note that when I reloaded my sbt console 
it seems the new dependency issued a warning about updating to scalaVersion 
2.10.5 for some reason. I hope this helps anyone else out there who runs into 
the issue! 



[scrimage]:https://github.com/sksamuel/scrimage
[this issue]:https://github.com/haraldk/TwelveMonkeys/issues/54
[useful list of common exceptions from batik]:http://thinktibits.blogspot.com/2012/12/apache-batik-common-runtime-exceptions.html