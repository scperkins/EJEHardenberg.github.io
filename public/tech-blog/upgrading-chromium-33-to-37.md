### Upgrading from Chromium 33 to 37

The other day I upgraded from [Chromium] version 33 to 37. Needless to say I broke a few things.

The flashplayer was screwed up, so I had to try to fix that. After trying some suggestions on symlinking things from /opt/chrome in and failing, then pulling down the latest stable release and manually copying out the flash player plugin and trying to use that. I did some more research and crawling of mailing lists and found a solution that worked.

[Here are the instructions I used] to install the ppa for chromium's pepper flash plugin. From yout terminal do the following:

    sudo add-apt-repository ppa:skunk/pepper-flash
    sudo apt-get update
    sudo apt-get install pepflashplugin-installer

The instructions then tell you to edit the /etc/chromium-browser/default profile and add in the following line to the script:

    . /usr/lib/pepflashplugin-installer/pepflashplayer.sh

That dot is important and supposed to be there btw. This fixed my problem until I restarted my computer. Then I had to add the line back in. At first I thought to myself, well I'll just put an echo into my `.bash_profile` and that will be that. But, since the file is owned by root it's not so simple. So I took a look at the profile itself. Upon investigation I found that in the profile it states this:

     This file is sourced by /bin/sh from 2 # /usr/bin/chromium-browser

So, I hopped over to `/usr/bin/chromium-browser` and checked out the script. Around line 76 I found a call to source the file. After investigating the script a bit I decided to add the following to my bash profile:

    #fix chromium flash player 
    export FLASH_VERSION=15.0.0.152
    export CHROMIUM_FLAGS="${CHROMIUM_FLAGS} --ppapi-flash-path=/usr/lib/pepflashplugin-installer/libpepflashplayer.so --ppapi-flash-version=$FLASH_VERSION"

But this is not the only way to fix it! On line 81 of the bin script it reads all the profiles in the `customizations` directory. So we could simply add the call to the pepflashplayer script in a custom profile.

So this is **/etc/chromium-browser/customizations/flash**:

    . /usr/lib/pepflashplugin-installer/pepflashplayer.sh

And then fix it up by running the following:

    $sudo chmod --reference=/etc/chromium-browser/default /etc/chromium-browser/customizations/flash 
    $ sudo chown --reference=/etc/chromium-browser/default /etc/chromium-browser/customizations/flash 

At that point you are no longer screwing with global exported flags and instead can use your custom profile instead. Neat right?



[Here are the instructions I used]:http://www.webupd8.org/2013/04/install-pepper-flash-player-for.html
[Chromium]:http://www.chromium.org/