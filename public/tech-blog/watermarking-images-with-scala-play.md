### Watermarking images in Scala with Play


Every now and again one finds themselves in the need to watermark image. This 
can be for any number of reasons. Whether you're tired of not getting cited 
by people using your content, or the boss has told you that all the images 
need to be watermarked. Doing this is pretty easy. In fact, if you're familiar 
with [ImageMagick] you know that they list examples of how to watermark images 
[directly on their website]. 

In Scala we can use the [sys package] to call to a shell, and this works well 
if you simply want to iterate over a directly and watermark each. Perhaps 
placing the watermarked image into a watermarks folder. Once you've done this 
you could use [apache] to check for a file in the watermarks folder, and if it 
doesn't exist generate it using a script or something similar. 

But if you're using [Play], you're probably not using apache, and instead are 
using the assets controller [as shown in the documentation]. If we wanted to 
_not_ use ImageMagick, and instead handle the watermarking on the fly from our 
application we can use the standard Java librarys that deal with images to do 
so. 

First off, we need to know how to grab the assets themselves. Looking around I 
found [this blog post about CDN assets] and adapted it into a simple controller 
method to pull the asset up:

_conf/routes_ 

	GET /watermarked/*file controllers.Watermark.show(path="/public", file)

_app/controllers/Watermark.scala_

	package controllers 

	import play.api._
	import play.api.mvc._

	import java.io.File
	import java.nio.file.{Files, Paths, Path}

	import java.awt.image.BufferedImage;
	import java.io.ByteArrayInputStream;
	import java.io.InputStream;
	import javax.imageio.ImageIO;

	import java.awt._
	import java.awt.image._
	import javax.imageio.ImageIO
	import javax.swing.ImageIcon
	import play.api.libs.iteratee._
	import scala.concurrent.ExecutionContext.Implicits.global

	object Watermark extends Controller {
		private def fullPath(asset : String, trueAssetPath : String = "public", aliasedAssetPath : String = "/assets") : Path = {
			Paths.get(asset			
			.replace(aliasedAssetPath, trueAssetPath) /* replace alias from routes with public dir (relative) */
			)
		}

		def show(assetAliasPath: String, file: String) = Action { implicit request =>
			val asset = routes.Assets.at(file).url

			val fileBytes = Files.readAllBytes(fullPath(asset))
			/* In a production system you'd want to check mime types and such! */
			val byteStream : java.io.InputStream = new ByteArrayInputStream(fileBytes)
			val bImageFromConvert :  BufferedImage = ImageIO.read(byteStream);
			byteStream.close
			val photo : ImageIcon = new ImageIcon(fileBytes)

			/* Bother Java to do the work for us */
			val waterMarkedImageBytes = Watermarker.watermark(bImageFromConvert, photo)

			if (waterMarkedImageBytes.length == 0) {
				BadRequest("Could not watermark image")
			} else {
				/* If you don't do the heads you'll just download the image in the
				 * browser as it will be of type application/octet-stream or something
				 * similar.
				 */
				Ok(waterMarkedImageBytes).withHeaders("Content-Type"->"image/jpeg")
			}
		}
	}

We'll get to the Watermarker class in a second, but first a coulple things to 
point out if you plan on using this code for anything. 

1. In a real system you'll want to check the [MimeType] of the file you're 
   reading. 
2. The content type header needs to be set on your sent image, otherwise if you 
   the file in the browser it will download it automatically. Linking via img 
   tags will show it fine though. Still, set the content type correctly.
3. The fullPath function does a simply replacement in order to find the path to 
   the file _relative_ to the application root.

Next up, the actual watermarking code. This I found from this [codebeach 
tutorial] and adapted into a simple helper class. Since [SBT] handles both java 
and scala code within the same application, we can use the following helper 
class to drive our watermarking:

	package controllers; //put in this package for convenience, move in real app

	import java.io.*;
	import java.awt.*;
	import java.awt.image.*;
	import javax.imageio.*;
	import javax.swing.ImageIcon;
	import java.awt.geom.Rectangle2D;
	import java.io.ByteArrayOutputStream;
	import javax.imageio.ImageIO;

	public class Watermarker {
		public static byte[] watermark(BufferedImage bufferedImage, ImageIcon photo) {
			try {

			    Graphics2D g2d = (Graphics2D) bufferedImage.getGraphics();

	            g2d.drawImage(photo.getImage(), 0, 0, null);

	            //Create an alpha composite of 50%
	            AlphaComposite alpha = AlphaComposite.getInstance(AlphaComposite.SRC_OVER,                                                               0.5f);
	            g2d.setComposite(alpha);

	            g2d.setColor(Color.white);
	            g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
	                                 RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

	            g2d.setFont(new Font("Arial", Font.BOLD, 30));

	            String watermark = "EthanJoachimEldridge.info";

	            FontMetrics fontMetrics = g2d.getFontMetrics();
	            Rectangle2D rect = fontMetrics.getStringBounds(watermark, g2d);

	            g2d.drawString(watermark,
	                            (photo.getIconWidth() - (int) rect.getWidth()) / 2,
	                            (photo.getIconHeight() - (int) rect.getHeight()) / 2);

	            //Free graphic resources
	            g2d.dispose();

	            /* Convert your image into a byte array */
	            ByteArrayOutputStream baos = new ByteArrayOutputStream();
	            /* We assume we're only working with jpg's, change if otherwise and handle accordingly */
	            ImageIO.write( bufferedImage, "jpg", baos );
				baos.flush();
				byte[] imageInByte = baos.toByteArray();
				baos.close();

				/* Return byte array since we can just write that straight out to the response */
	            return imageInByte;
	        } catch (java.io.IOException e) {
	        	return new byte[0];
	        }
		}
	}

This is pretty much verbatim what's available from codebeach besides changing 
the watermark string and returning a byte array. Make sure to close any of the 
streams you open when doing graphics code! Not doing so can cause leaks or the 
request to hang. Neither of these things are things you want in an application. 

To test this code out, make a Play application and throw these classes into the 
application in the controllers folder. Once the route is set up and you have an 
image in the public folder, navigate to _localhost:9000/watermarked/filename_ 
and you should see the image appear with a transparent watermark of whatever 
text you placed into the _watermark_ string. 

When I first started in on making this project I looked into [filters], and 
used the Content-Type of the result to check if a watermark should be applied 
or not. That part worked fine, however creating a new body to the Result object 
proved a bit too much of a challenge for my current scala abilities. So I gave 
up on that for now. Perhaps I'll look into again later, once I fully understand 
how to manipulate [Iteratees], as being able to have a filter watermark all 
image assets without needing a new url would be a better solution then not 
using the Assets controller at all.


[ImageMagick]:http://www.imagemagick.org
[directly on their website]:http://www.imagemagick.org/Usage/annotating/#wmark_text
[sys package]:http://www.scala-lang.org/api/2.9.2/scala/sys/process/package.html
[Play]:http://www.playframework.com
[apache]:http://apache.org
[as shown in the documentation]:https://www.playframework.com/documentation/2.0/Assets
[this blog post about CDN assets]:http://www.jamesward.com/2014/04/29/optimizing-static-asset-loading-with-play-framework
[MimeType]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.libs.MimeTypes$
[codebeach tutorial]:http://www.codebeach.com/2008/02/watermarking-images-in-java-servlet.html
[SBT]:http://scala-sbt.org
[filters]:https://www.playframework.com/documentation/2.2.x/ScalaHttpFilters
[Iteratees]:http://mandubian.com/2012/08/27/understanding-play2-iteratees-for-normal-humans/