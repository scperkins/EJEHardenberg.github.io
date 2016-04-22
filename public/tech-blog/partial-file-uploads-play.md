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
define the controller action so that we can get the file chunk from the 
posted byte array via `request.body.file("file")`. For the file test 
handler we can simply `bindFromRequest` and use the unique identifier 
and chunk number to see if we've already processed it.

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
`FileUploadService`. If we implement the success method for the `fileUploadInfoForm` 
fold as calling down to the FileUploadService or returning an error, then we can 
finish up the controller:
	
	request.body.file("file") match {
		case None => BadRequest("No file")
		case Some(file) =>
			val bytes = Files.readAllBytes(file.ref.file.toPath())
			fileUploadService.savePartialFile(bytes, fileUploadInfo)
			file.ref.clean()
			Ok
	}

The `request.body.file` provides our code with a [TemporaryFile] that we 
can use in our request. Since our [FileUploadService] works on byte arrays, 
we can use the [Files] class to convert the [File] into what we need. 
Once we have that, it's easy to save it. Expanding our example of how to 
use the [RandomAccessFile], we can see the `savePartialFile` method is 
very simple:

	def savePartialFile(filePart: Array[Byte], fileInfo: FileUploadInfo) {
		if (filePart.length != fileInfo.resumableChunkSize) {
			return
		}
		val partialFile = new RandomAccessFile(fileNameFor(fileInfo), "rw")
		val offset = (fileInfo.resumableChunkNumber - 1) * fileInfo.resumableChunkSize

		try {
			partialFile.seek(offset)
			partialFile.write(filePart, 0, filePart.length)
		} finally {
			partialFile.close()
		}

		val key = fileNameFor(fileInfo)
		if (uploadedParts.containsKey(key)) {
			val partsUploaded = uploadedParts.get(key)
			uploadedParts.put(key, partsUploaded + fileInfo)
		} else {
			uploadedParts.put(key, Set(fileInfo))
		}
	}

`uploadedParts` is our [ConcurrentHashMap] defined during the construction 
of the class. In a more robust implementation, we'd define the map as a 
singleton or use an application wide cache to store the parts. But for now, 
defining the map inside our class as a property, and then having the controller 
be an `object` will work fine as a simple example. With this code, we're 
able to handle the two types of requests that ResumableJS will send us.

#### Example front end for ResumableJS

ResumableJS is a well written library in my opinion. Namely the API is clear 
and the events are well documented. Before we get to the javascript we 
need the page body though. Since this post is focused mainly on the back
end code and a simple implementation of the front end I didn't make any 
special styling for this, so the interface is rather sparse.

	<body>
		<a id="browseButton" href="#">Browse and Upload</a>
		<a id="upLoadButton" href="#">Upload</a>
		<a id="pauseButton" href="#">Pause Uploads</a>
		<a id="cancelButton" href="#">Cancel All</a>
		<span id="errorMsg" style="color: red;"></span>
		<div id="uploadprogress">0 %</div>
		<ul id="filestobeuploaded">
		</ul>
	</body>
	<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/resumable.js/1.0.2/resumable.js">


<img src="/images/tech-blog/resumablejs-front-end-1.jpg"/>

The first thing to do is intialize the library:

		var r = new Resumable({
			target:'/upload', 
			query:{}
		});
		r.assignBrowse(document.getElementById('browseButton'));

And bind the upload button to one of our anchors:

	document.getElementById('upLoadButton').onclick = function(){
		r.upload();
	}

And you're done. Well, if you're looking to create something which offers 
no feedback to the users you are. But we want to show the users the files 
they've selected for uploading. This is easy enough if we hook into the 
`fileAdded` event:

	r.on('fileAdded', function(file){ 
		addFileToList(file);
	});

The method `addFileToList` is probably the longest part of our code simply 
because we need to create and add elements to the page:

	var filesSpace = document.getElementById('filestobeuploaded');
	function addFileToList(file) {
		var li = document.createElement('li');

		var progressBar = document.createElement('span');
		progressBar.textContent = '0 %';
		progressBar.id = file.uniqueIdentifier + "-progress";

		var fileNameSpan = document.createElement('span');
		fileNameSpan.textContent = file.fileName;

		var cancelButton = document.createElement('a');
		cancelButton.href ='#';
		cancelButton.textContent = 'Cancel';
		cancelButton.onclick = function() {
			file.cancel();
			filesSpace.removeChild(li);
		}
		
		li.setAttribute('style','border: solid black thin;');
		li.appendChild(fileNameSpan);
		li.appendChild(document.createElement('br'));
		li.appendChild(progressBar);
		li.appendChild(document.createElement('br'));
		li.appendChild(cancelButton);

		filesSpace.appendChild(li);
	}

Our display of each file shows the file name, a progress indicator, and 
a cancel button. Canceling a file is simply a matter of calling  the 
`cancel` method on ResumableJS's file object that is passed to the event. 
This handles stopping the upload and removing the file from the list of 
files to be uploaded by ResumableJS, our front end code simply deletes 
the entire `li` element that we build in the above method. The progress 
`span` is given an identifier that we will use from the `fileProgress` 
event to update the progress shown to the user:

	r.on('fileProgress', function(file) {
		var progressBarToUpdate = document.getElementById(file.uniqueIdentifier + "-progress");
		progressBarToUpdate.textContent = (file.progress(false) * 100.00) + '%';
	});

As noted in the documentation, the method `progress` on the file instance:

>Returns a float between 0 and 1 indicating the current upload progress of the file. If relative is true, the value is returned relative to all files in the Resumable.js instance.

Since we're showing individual progress we use `false` for the relative 
parameter. Since users might be interested in knowing the total progress 
of the downloads we can show that to them too:

	var progress = document.getElementById('uploadprogress');
	r.on('progress', function() {
		progress.textContent = (r.progress() * 100.00)+'%';
	});

At this point we have a fully functioning asynchronous upload page. But 
if we wanted that we could have used any front end library to do that;
what makes ResumableJS special is that it supports _pausing_ an upload 
as well and resuming it later. 

	document.getElementById('pauseButton').onclick = function(){
		r.pause();
	}

If you pause an upload you can resume it at any time by clicking the 
upload button again if you have the page still open in your browser. The 
nice thing about handling the test requests means that we could upload 
part of the file now, then come back hours later and continue the upload. 
This is what ResumableJS is designed for after all, spotty networks and 
fault tolerance in your uploads.

Let's hook up the rest of our HTML to the library:

	document.getElementById('cancelButton').onclick = function() {
		r.cancel();
	}

	var errorMsg = document.getElementById('errorMsg');
	r.on('cancel', function(file) {
		var anchors = filesSpace.getElementsByTagName('a');
		for (var i = anchors.length - 1; i >= 0; i--) {
			anchors[i].click();
		};
		errorMsg.textContent = 'Upload canceled';
	});

	r.on('error', function (message, file) {
		errorMsg.textContent = message;
	});

With that in place the cancel button works and we show any errors that 
the library comes across in the error span. There are a few other events 
in the library that you can handle (like file upload success), but you 
can see that [on github]. 

[resumablejs]:http://resumablejs.com/
[wrote up uploading binaries in play]:/tech-blog/upload-binary-data-play-exif
[RandomAccessFile]:https://docs.oracle.com/javase/7/docs/api/java/io/RandomAccessFile.html
[loaded from a CDN]:https://cdnjs.cloudflare.com/ajax/libs/resumable.js/1.0.2/resumable.js
[good documentation]:http://resumablejs.com/
[My entire HTML file]:https://github.com/EdgeCaseBerg/play-resumablejs-upload/blob/master/app/views/index.scala.html
[FileUploadService]:https://github.com/EdgeCaseBerg/play-resumablejs-upload/blob/master/app/service/FileUploadService.scala
[ConcurrentHashMap]:https://docs.oracle.com/javase/7/docs/api/java/util/concurrent/ConcurrentHashMap.html
[TemporaryFile]:https://www.playframework.com/documentation/2.3.x/api/scala/index.html#play.api.libs.Files$$TemporaryFile
[Files]:https://docs.oracle.com/javase/7/docs/api/java/nio/file/Files.html
[File]:https://docs.oracle.com/javase/7/docs/api/java/io/File.html
[on github]:https://github.com/EdgeCaseBerg/play-resumablejs-upload
[github issue on ResumableJS]:https://github.com/23/resumable.js/issues/135#issuecomment-31123690