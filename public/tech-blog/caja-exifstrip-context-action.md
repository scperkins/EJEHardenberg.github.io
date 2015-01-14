### Added an exifstrip command to Caja

I wrote about how to use exiftools to strip image meta data from images
in nautilus [before]. But not everyone use's nautilus. If you happen to
be using [Caja] then it's pretty easy to create your own context menu
addition easily. 

Caja scripts are stored in your **~/.config/caja/scripts** directory,
and adding any script, then making it executable will cause it to appear
in the context menu under "scripts". So to add your own exif stripping
tool to your menus, you can add the following:

**~/.config/caja/scripts/strip-exif**

	#!/bin/sh
	for f in $CAJA_SCRIPT_SELECTED_FILE_PATHS
	do
		mimetype $f | grep "image" && exiftool -all= $f
	done

Once done, a quick `chmod a+x ~/.config/caja/scripts/strip-exif` will
make it executable and you'll be off to the races. No big GUI messes
like nautilus, just simple scripting. If you like adding context menus
or scripting, a good list of the variables available to you is located 
[here].


[Caja]:http://community.linuxmint.com/software/view/caja
[before]:http://www.ethanjoachimeldridge.info/tech-blog/exifstrip-context-nautilus
[here]:http://translate.google.com/translate?hl=en&sl=zh-TW&u=http://misawascriptkid.blogspot.com/2012/06/caja.html&prev=search
