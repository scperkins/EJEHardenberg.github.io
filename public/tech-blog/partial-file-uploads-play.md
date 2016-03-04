### Partial File upload's and Play

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


[resumablejs]:http://resumablejs.com/
[wrote up uploading binaries in play]:/tech-blog/upload-binary-data-play-exif