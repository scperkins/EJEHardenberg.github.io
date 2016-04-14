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

#### Using ResumableJS

ResumableJS can be [loaded from a CDN] onto your page if you don't want to 
host it yourself. It also is fairly easy to use and has [good documentation].
[My entire HTML file] was a little over 100 lines of code and was pretty small.
Most of the work is done on the back-end to support the two types of requests
that ResumableJS will make. 

1. The upload of a file chunk
2. Testing if a file chunk has already been updated

Both of these requests will be sent to the `target` url, the first via `POST`
and the second via `GET`. Besides the file chunk in the body, both methods 
share the same parameters. The `GET` request looks something like this:

	http://localhost:9000/upload?resumableChunkNumber=1&resumableChunkSize=1048576&resumableCurrentChunkSize=1048576&resumableTotalSize=7185630&resumableType=video%2Fwebm&resumableIdentifier=7185630-webm&resumableFilename=%E2%96%B3.webm&resumableRelativePath=%E2%96%B3.webm&resumableTotalChunks=6




[resumablejs]:http://resumablejs.com/
[wrote up uploading binaries in play]:/tech-blog/upload-binary-data-play-exif
[RandomAccessFile]:https://docs.oracle.com/javase/7/docs/api/java/io/RandomAccessFile.html
[loaded from a CDN]:https://cdnjs.cloudflare.com/ajax/libs/resumable.js/1.0.2/resumable.js
[good documentation]:http://resumablejs.com/
[My entire HTML file]:https://github.com/EdgeCaseBerg/play-resumablejs-upload/blob/master/app/views/index.scala.html