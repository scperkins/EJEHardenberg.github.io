### Aspect Ratios and Math 

The web needs images of all sizes to work. For example, when you load 
a gallery view of images you're served thumbnail sized images, when 
you click through to view those you get to see the full sized image. 
A lot of work goes into cropping, resizing, and generating all of 
these images. Sometimes it's some poor intern sitting at Photoshop 
or Gimp, other times it's an editor of some kind. And occasionally 
us [tech workers get to throw our scripting skills at it].

While there are some image services out there (such as CDN integrated 
ones like [Akamai]), or services you can [run inside apache], if you 
want to keep custom tracking you often need to do a good amount of work
yourself. Allowing a user to index metadata against a master image then 
generate more images is just one place where most image services often 
fall short of meeting the needs of specialized workplaces. 

So what do you do? Well, besides build your own image service, there's 
not too much you can do! So let's say you decide to setup a really basic 
service for yourself. Something simple like: allow a user to upload a 
master record then retrieve a few predefined presets of crops? Or what 
about something even simpler, resizing the image to presets? When it comes 
to the content, you often need differing _aspect ratios_ of images in 
order to maximize your page space. Portrait, landscape, wide angle. You 
name it, there's a proper aspect ratio to be displaying this stuff at. 

It's taken a bit to get to the code, but I'd like to share a building 
block with you. First, let's assume three simple ratios. 1:1, 4:9, and 
16:9. Or, Square, Portrait, and Landscape. In scala we could define 
these as an enumeration like so:

	object AspectRatio extends Enumeration {
		type Ratio = Value
		val OneToOne, FourToNine, SixteenToNine = Value
	}

Which is a good start, but that doesn't help us much. After all, if I'm 
working with an aspect ratio and resizing an image down, I probably want 
to work with _numbers_. So let's add in an implicit class that will give 
us a way to get back something useful: 

	object AspectRatio extends Enumeration { 
		...
		implicit class AspectRatioToRuple(ratio: AspectRatio.Ratio) {
			def asTuple : Tuple2[Int,Int] = ratio match {
				case OneToOne => (1,1)
				case FourToNine => (4,9)
				case SixteenToNine => (16,9)
			}
		}
	}

Great! So now we can do things like this in the console: 

	import AspectRatio._
	OneToOne.asTuple // => (1,1)

Which is great for any math we might need to do with the actual numeric 
values associated with our ratios. What about the other way? Going from 
a tuple `(1,1)` to the `OneToOne` ratio? We'll need another implicit 
class:

	import java.lang.IllegalArgumentException
	object AspectRatio extends Enumeration {
		...
		implicit class Tuple2ToAspectRatio(tuple: Tuple2[Int,Int]) {
			def asAspectRatio : AspectRatio.Ratio = tuple match {
				case (1,1) => OneToOne
				case (4,9) => FourToNine
				case (16,9) => SixteenToNine
				case _ => throw new IllegalArgumentException(s"Could not find matching aspect ratio for tuple ${tuple}")
			}
		}
	}

Great you say! Now you can convert back and forth between numeric and symbolic 
representations of your aspect ratios. But wait, what if you're trying to tell 
what aspect ratio a given picture is? Let's pretend we have some simple `Image` 
class that has both width and height defined, if we simply do this:

	case class Image(width: Int, height: Int)
	val i = Image(250,250)
	(i.width,i.height).asAspectRatio

We'll be greeted by our `IllegalArgumentException`. Even though we as humans know 
that it's a 1:1 ratio here. This is a problem anyone who's gone through a discrete 
mathematics course knows how to solve though. What we're really looking for is the 
[Greatest Common Denominator], or GCD. Luckily for me I stumbled across a rather 
nice [blog post about a Fraction class] by [Andrei N. Ciobanu] and this provides us 
a really nice way to normalize the width and height of our image. The only issue of 
course is that the Fraction class isn't a case class so it doesn't have an [extractor] 
defined. But of course we can update the code to allow this like so: 

	/** Private Class to represent a simple fraction in simplest form
	 * 
	 * @note Fraction class attribution: Andrei N. Ciobanu 
	 *
	 * @param n The numerator of the fraction 
	 * @param d The denominator of the fraction
	 */
	class Fraction(n: Int, d: Int) {
		// It makes no sense to have the denominator 0
		require(d != 0)

		private val g = gcd(n, d)
		val numerator : Int = n / g
		val denominator : Int = d / g

		// Determines the greatest common divisor of two numbers
		private def gcd(a: Int, b: Int) : Int =
			if (b == 0) a else gcd(b, a % b)

		override def toString =
			numerator + "/" + denominator
	}

	/* Our enhancement to the class to support pattern matching */
	object Fraction {
		def apply(tuple2: Tuple2[Int,Int]): Fraction = new Fraction(tuple2._1,tuple2._2)
		def unapply(obj: Fraction): Option[Tuple2[Int,Int]] = Some((obj.numerator, obj.denominator))
	}

With this in place we can rewrite `asAspectRatio` to handle arbitrary image 
sizes:

	object AspectRatio extends Enumeration {
		...
		implicit class Tuple2ToAspectRatio(tuple: Tuple2[Int,Int]) {
			def asAspectRatio : AspectRatio.Ratio = Fraction(tuple) match {
				case Fraction(1,1) => OneToOne
				case Fraction(4,9) => FourToNine
				case Fraction(16,9) => SixteenToNine
				case _ => throw new IllegalArgumentException(s"Could not find matching aspect ratio for tuple ${tuple}")
			}
		}
	}

And now we can see that `(250,250).asAspectRatio` returns `OneToOne` as aspected. 

You might be asking yourself, Ok, so how does this help me with making an Image 
Service for the boss learing down my neck? Simple. If you're designing your system 
to _cache_ the generated images, you'll want to keep track of that. By using some 
of the above code you could easily check to see if a requested image can be cropped 
or sized to your predefined aspect ratios. If not you can deny the request, if so, 
you could key your database on which aspect ratios you support and retrieve a url 
to the cached content, or generate it and store the content, then mark it in the 
database. Something like this: 

1. Request for 4:9 of image X 
2. Database lookup to see if cache url exists
3. If cache exists, direct the user there. Otherwise:
4. Retrieve the master image and use the numeric versions of the crop to manipulate the image
5. Deny the request if you can't manipulate the image to the right size
5. Cache the generated content onto a CDN
6. Store a record keyed by the image's ID and aspect ratio with the url to your database for later

A workflow something like this would probably work. There's obvious more details 
to go in there of course, but defining a way to switch between symbolically and 
mathematically manipulating aspect ratios can help out when you start doing more 
complicated things. 

**Note:** euclids GCD algorithm is good but it isn't the fastest, so if you're 
concerned for performance, feel free to look up more performant versions. Such as 
Stein’s Algorithm.


[tech workers get to throw our scripting skills at it]:https://codeascraft.com/2010/07/09/batch-processing-millions-of-images/
[Akamai]:https://www.akamai.com/us/en/solutions/intelligent-platform/cloudlets/image-converter.jsp
[run inside apache]:https://github.com/beetlebugorg/mod_dims
[Greatest Common Denominator]:https://en.wikipedia.org/wiki/Greatest_common_divisor
[Andrei N. Ciobanu]:http://andreinc.net/about-me/
[blog post about a Fraction class]:http://andreinc.net/2010/12/28/fraction-reduction-in-scala/
[extractor]:danielwestheide.com/blog/2012/11/21/the-neophytes-guide-to-scala-part-1-extractors.html