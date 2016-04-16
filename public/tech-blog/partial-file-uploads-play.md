### Partial File upload's and Play

#### ResumableJS

The other day I stumbled across [resumablejs] and was thinking to myself 
that when dealing with large files this would be a really nice thing to 
have. Since I [wrote up uploading binaries in play] before, I figure'd 
that writing about how to upload large files would be a reasonable thing 
to continue with. 

Now, resumablejs has more features than just splicing a file and sending 
those chunks along. Through its event API you can monitor progress, 
errors, new files, cancel's and completions. This means that if you wanted 
to you could build a very robust uploading system that let people upload 
parts of files while their network was spotty, or allow them to pause 
their uploads if they needed to use their bandwidth for other things. It's 
a very well defined API that is designed to do one thing and do it well. 
The nice thing about properly defined API's is that it's easy to code 
against them.

#### File Combination Strategy

ResumableJS uploads files in chunks, so once the parts are on the server 
we'll need to combine them in some way. There are two basic options:

1. Store each part individually then combine them once all pieces are present
2. Use a [RandomAccessFile] to place the chunks in the proper position inside of one file, and once all pieces are present to cease the upload.

For simplicities sake, the [RandomAccessFile] is the way I've chosen to 
go for this. Mainly because handling a single file rather than attempting 
to monitor many seems like it would be easier to do. We can also easily
jump to an offset within the file by using the `seek` method. Or verify 
that all the pieces of a file are there and match if we wanted to. 


_How to write some bytes to a part of a file_

	import java.io.{ File, RandomAccessFile }

	val filePart: Array[Byte] = // the bytes for the piece of the file
	val partialFile = new RandomAccessFile("myfilename.ext", "rw")
	val offset = //compute offset inside of file for this part
	try {
		partialFile.seek(offset)
		partialFile.write(filePart, 0, filePart.length)
	} finally {
		partialFile.close()
	}

The above code is part of the [FileUploadService] which handles a `RandomAccessFile`. 
The offset is created with the simple formula of `(Chunk # -1) * ChunkSize`. 
The `-1` is because ResumableJS counts from 1 for the chunks. Note that we 
don't need to worry about the last chunk's `ChunkSize` being different because 
ResumableJS always passes the general chunk size, and not the length of the 
byte array it's sending:

_From the Docs:_

>resumableChunkSize: The general chunk size. Using this value and resumableTotalSize you can calculate the total number of chunks. Please note that the size of the data received in the HTTP might be lower than resumableChunkSize of this for the last chunk for a file.

So the only other thing we need to worry about is keeping track of _which_ parts
of a file we've uploaded and that we've got a consistent filename. As you'll see 
in the next part, ResumableJS gives us a unique identifier for each _whole_ file 
it's uploading, so we can rely on that as both a key to a hashmap, and as a name.
Inside the `FileUploadService` we can use a [ConcurrentHashMap] to keep track of 
the part's we've uploaded: 

_Keeping track of file upload parts_

	val uploadedParts: ConcurrentMap[String, Set[FileUploadInfo]] = new ConcurrentHashMap(8, 0.9f, 1)

#### Handling ResumableJS requests

ResumableJS can be [loaded from a CDN] onto your page if you don't want to 
host it yourself. It's also fairly easy to use and has [good documentation].
[My entire HTML file] was a little over 130 lines of code and was pretty small.
Most of the work is done on the back-end to support the two types of requests
that ResumableJS will make. 

1. The upload of a file chunk
2. Testing if a file chunk has already been uploaded

Both of these requests will be sent to the `target` url, the first via `POST`
and the second via `GET`. Besides the file chunk in the body, both methods 
share the same parameters. The `GET` request looks something like this:

	http://localhost:9000/upload?resumableChunkNumber=1&resumableChunkSize=1048576&resumableCurrentChunkSize=1048576&resumableTotalSize=7185630&resumableType=video%2Fwebm&resumableIdentifier=7185630-webm&resumableFilename=%E2%96%B3.webm&resumableRelativePath=%E2%96%B3.webm&resumableTotalChunks=6

You can see some useful parameters right away, namely the identifier and the 
chunk related ones. Since we're using play, we can bind these to an object 
very easily:

_Our object: FileUploadInfo.scala_

	package model

	case class FileUploadInfo(
			val resumableChunkNumber: Int,
			val resumableChunkSize: Int,
			val resumableTotalSize: Int,
			val resumableIdentifier: String,
			val resumableFilename: String
	) {
		def totalChunks = Math.ceil(resumableTotalSize.toDouble / resumableChunkSize.toDouble)
	}

_The Bindings for play: Forms.scala_

	package form

	import play.api.data._
	import play.api.data.Forms._

	import model._

	object Forms {
		def fileUploadInfoForm = Form(
			mapping(
				"resumableChunkNumber" -> number,
				"resumableChunkSize" -> number,
				"resumableTotalSize" -> number,
				"resumableIdentifier" -> nonEmptyText,
				"resumableFilename" -> nonEmptyText
			)(FileUploadInfo.apply)(FileUploadInfo.unapply)
		)
	}

And then inside of a controller we can bind the incoming values using 
`bindFromRequest`:

	Forms.fileUploadInfoForm.bindFromRequest.fold(
		formWithErrors => {...},
		fileUploadInfo => {...}
	)

For the upload handler we'll use `Action(parse.multipartFormData)` to 
define the action so that we can get the file chunk from the posted byte 
array via `request.body.file("file")`. For the file test handler we can 
simply `bindFromRequest` and use the unique identifier and chunk number 
to see if we've already processed it.

	_Handling test requests for ResumableJS_:

	def uploadTest = Action { implicit request =>
		Forms.fileUploadInfoForm.bindFromRequest.fold(
			formWithErrors => {
				BadRequest(formWithErrors.errors.mkString("\n"))
			},
			fileUploadInfo => {
				if (fileUploadService.isPartialUploadComplete(fileUploadInfo)) {
					Ok
				} else {
					NotFound
				}
			}
		)
	}

Where `isPartialUploadComplete` is simply:

	def isPartialUploadComplete(fileInfo: FileUploadInfo): Boolean = {
		val key = fileNameFor(fileInfo)
		uploadedParts.contains(key) && uploadedParts.get(key).contains(fileInfo)
	}

You can use the `resumableIdentifier` as a key, or the path to the file you're 
creating (what my `fileNameFor` method does). But either way, our check for if 
the file is done uploading or not is based on the presence of the file chunk 
being in the `Set` of chunks tracked by the `ConcurrentHashMap` within the 
`FileUploadService`.

[resumablejs]:http://resumablejs.com/
[wrote up uploading binaries in play]:/tech-blog/upload-binary-data-play-exif
[RandomAccessFile]:https://docs.oracle.com/javase/7/docs/api/java/io/RandomAccessFile.html
[loaded from a CDN]:https://cdnjs.cloudflare.com/ajax/libs/resumable.js/1.0.2/resumable.js
[good documentation]:http://resumablejs.com/
[My entire HTML file]:https://github.com/EdgeCaseBerg/play-resumablejs-upload/blob/master/app/views/index.scala.html
[FileUploadService]:https://github.com/EdgeCaseBerg/play-resumablejs-upload/blob/master/app/service/FileUploadService.scala
[ConcurrentHashMap]:https://docs.oracle.com/javase/7/docs/api/java/util/concurrent/ConcurrentHashMap.html