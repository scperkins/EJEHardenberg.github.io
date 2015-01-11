### Installing Gentoo

Today I decided I'd try out a different distribution of linux than my 
usual. After reading through the [Gentoo handback], I decided to roll
with Gentoo.

Of course, I decided to try everything out first and created an image 
in VirtualBox and then downloaded the [minimal installation of gentoo].
I ran into a problem with VirtualBox, but luckily [the internet had me covered].

Next up, I grabbed the [signature of the iso] and verified it.

    $gpg --recv-keys 0xBB572E0E2D182910
    gpg: requesting key 2D182910 from hkp server keys.gnupg.net
	gpg: key 2D182910: public key "Gentoo Linux Release Engineering (Automated Weekly Release Key) <releng@gentoo.org>" imported
	gpg: 3 marginal(s) needed, 1 complete(s) needed, PGP trust model
	gpg: depth: 0  valid:   1  signed:   7  trust: 0-, 0q, 0n, 0m, 0f, 1u
	gpg: depth: 1  valid:   7  signed:   0  trust: 7-, 0q, 0n, 0m, 0f, 0u
	gpg: next trustdb check due at 2018-09-18
	gpg: Total number processed: 1
	gpg:               imported: 1  (RSA: 1)

    $gpg --verify install-x86-minimal-20141209.iso.DIGESTS.asc 
	gpg: Signature made Tue 09 Dec 2014 07:49:09 AM EST using RSA key ID 2D182910
	gpg: Good signature from "Gentoo Linux Release Engineering (Automated Weekly Release Key) <releng@gentoo.org>"
	gpg: WARNING: This key is not certified with a trusted signature!
	gpg:          There is no indication that the signature belongs to the owner.
	Primary key fingerprint: 13EB BDBE DE7A 1277 5DFD  B1BA BB57 2E0E 2D18 2910

I then checked that the fingerprint matched the one on the [Gentoo Website] 
and then checked that the ISO file I had downloaded matched the hash within the 
digest file:

	$grep -A 1 -i sha512 install-x86-minimal-20141209.iso.DIGESTS.asc 
	# SHA512 HASH
	4d6b7e6ec411b8536221ea5a5c5e7f2d0fa766d99727a6593bcbffa0aff0409a84486306217a6c208cc8b1504c3088711838fec57e0af2c5338e90978342b7bf  install-x86-minimal-20141209.iso
	--
	# SHA512 HASH
	bfc0384646b3b38935bd272912d56cbc10f7a05f612073023205dc2ffbf9012f8e189d1bc8c7b8afbef92e2bf336cd5e2a0693894775573f11800e7e0a48f90e  install-x86-minimal-20141209.iso.CONTENTS

	sha512sum install-x86-minimal-20141209.iso
	4d6b7e6ec411b8536221ea5a5c5e7f2d0fa766d99727a6593bcbffa0aff0409a84486306217a6c208cc8b1504c3088711838fec57e0af2c5338e90978342b7bf  install-x86-minimal-20141209.iso

Once done I started up VirtualBox and booted the gentoo image. On the first screen,
the kernel select I accidently waited looking at it a bit too long and had to 
reset the VM, but then hit F1 for the kernel's list and chose gentoo. Once I 
had done this a happy penguin appeared in front of me and a bunch of text started
flowing by.

<img src="/images/tech-blog/gentoo-1.png" >

And then it got stuck while trying to load the SATA. And sat there for a while 
not doing anything and being frozen.

<img src="/images/tech-blog/gentoo-frozen.png" >

I tried out booting with `gentoo`, `gentoo-nofb`, and `gentoo-nofb nodetect` and 
it just seemed like it was sitting and waiting. So then it was time to check if
VirtualBox was stuck, a quick `sudo sysdig proc.name=VirtualBox` told me, no?

	...
	207470 22:46:34.128462638 0 VirtualBox (13696) > recvfrom fd=25(<u>) size=4096 
	207471 22:46:34.128462972 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207472 22:46:34.128464051 0 VirtualBox (13696) > poll fds=20:e1 24:u1 25:u1 29:u1 18:u1 30:p1 35:u1 36:u1 timeout=0 
	207473 22:46:34.128465099 0 VirtualBox (13696) < poll res=0 fds= 
	207474 22:46:34.128465571 0 VirtualBox (13696) > read fd=20(<e>) size=16 
	207475 22:46:34.128465881 0 VirtualBox (13696) < read res=-11(EAGAIN) data= 
	207476 22:46:34.128466612 0 VirtualBox (13696) > recvfrom fd=18(<u>) size=4096 
	207477 22:46:34.128466931 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207478 22:46:34.128468874 0 VirtualBox (13696) > recvfrom fd=18(<u>) size=4096 
	207479 22:46:34.128469221 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207480 22:46:34.128470133 0 VirtualBox (13696) > recvfrom fd=25(<u>) size=4096 
	207481 22:46:34.128470424 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207482 22:46:34.128471513 0 VirtualBox (13696) > poll fds=20:e1 24:u1 25:u1 29:u1 18:u1 30:p1 35:u1 36:u1 timeout=0 
	207483 22:46:34.128472509 0 VirtualBox (13696) < poll res=0 fds= 
	207484 22:46:34.128473025 0 VirtualBox (13696) > read fd=20(<e>) size=16 
	207485 22:46:34.128473347 0 VirtualBox (13696) < read res=-11(EAGAIN) data= 
	207486 22:46:34.128474079 0 VirtualBox (13696) > recvfrom fd=18(<u>) size=4096 
	207487 22:46:34.128474410 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207488 22:46:34.128476533 0 VirtualBox (13696) > recvfrom fd=18(<u>) size=4096 
	207489 22:46:34.128476845 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	207490 22:46:34.128477776 0 VirtualBox (13696) > recvfrom fd=25(<u>) size=4096 
	207491 22:46:34.128478073 0 VirtualBox (13696) < recvfrom res=-11(EAGAIN) data= tuple=NULL 
	...

So I reset my VM and decided to enable the debug logging (something I should have 
done in the first place) and to tell gentoo not to bother with SATA. Running 
`gentoo nosata debug` got me to the point where it tried to scan for `raid456`,
and then it hung. 

<img src="/images/tech-blog/gentoo-raid456.png" >

So I reset the VM again and ran `gentoo nosata noload=raid456 debug`, it got 
farther this time, all the way to `raid5`. So maybe it was a problem with the
raid modules themselves? I scanned the Handbook and found the option `nodmraid`, 
reset the VM and tried running `gentoo nosata nodmraid debug`. 

This apparently wasn't what I thought it was, so I reset and started looking through
the handbook again before deciding to just list the modules I didn't need. This 
is what I ended up with:

	gentoo noload=ahci,ata_piix,raid456,raid5,raid6,btrfs,e1000 debug

After doing this, the system loaded and dropped me in on a console. My user id 
was 0 (`whoami` told me so but didn't have a name for the user). The weird thing
was that my prompt complained as it dropped me on my head:

	BusyBox v1.20.0 (built in shell ash)
	/bin/ash: can't access tty; job control turned off
	#

At this point I had to wonder what was going on, and so I checked the internet 
for [people having the same problem], checking `/dev/tty` got me a permission 
denied message, it didn't seem like a size problem like [some users experienced],
but a permissions one. Running the same command without the debug option gave me
the error: "making tmpfs for /newroot" and "segmentation fault" right underneath.

So something was clearly up. Looking at the Virtualbox settings, I realized the 
IDE controller setting was set to **ahci**, but wait didn't I have to say `noload=ahci`
to get to the shell in the first place? Looking in my host system, I wondered if
maybe I didn't have the drivers there, so it was having trouble with that? So 
I looked for clues:

	$locate ahci
	/lib/modules/3.2.0-23-generic/kernel/drivers/ata/acard-ahci.ko
	/lib/modules/3.2.0-23-generic/kernel/drivers/ata/ahci_platform.ko
	/usr/src/linux-headers-3.2.0-23/include/linux/ahci_platform.h
	/usr/src/linux-headers-3.2.0-23-generic/include/config/sata/ahci
	/usr/src/linux-headers-3.2.0-23-generic/include/config/sata/ahci.h
	/usr/src/linux-headers-3.2.0-23-generic/include/config/sata/acard/ahci.h
	/usr/src/linux-headers-3.2.0-23-generic/include/config/sata/ahci/platform.h
	/usr/src/linux-headers-3.2.0-23-generic/include/linux/ahci_platform.h

Looking at the `include/config` directories, I noticed something important about
the ahci files. Namely that they were all emtpy. Returning to the handbook, I 
read over the boot parameters again, trying out `ide=nodma` since the handbook
statues:

<blockquote>
	If the system is having trouble reading from the IDE CDROM, try this option.
</blockquote>

I also tried any options (such as `nodetect`) that hinted at being able to trouble
shoot issues with the CDROM. Staring at the screen, I began to wonder if it wasn't
the cd rom that was the problem, but the space to mount it. There was a line 
stating that there was a segmentation fault creating `tmpfs for /newroot` after 
all.

But all in all, no matter what settings I tried, changing the IDE to primary, to 
slave, to reading the init script and trying to run the mounting of the cd myself,
it just didn't work. 

You've beaten me for now virtualbox!

<img src="/images/tech-blog/gentoo-beaten.png" />










[Gentoo handback]:http://wiki.gentoo.org/wiki/Main_Page
[minimal installation of gentoo]:http://ftp.ucsb.edu/pub/mirrors/linux/gentoo/releases/x86/current-iso/
[the internet had me covered]:http://askubuntu.com/a/220778/254629
[signature of the iso]:http://ftp.ucsb.edu/pub/mirrors/linux/gentoo/releases/x86/current-iso/install-x86-minimal-20141209.iso.DIGESTS.asc
[Gentoo Website]:https://www.gentoo.org/proj/en/releng/
[people having the same problem]:http://www.linuxquestions.org/questions/ubuntu-63/bin-sh-can%27t-access-tty%3B-job-control-turned-off-474493/
[some users experienced]:http://forums.gentoo.org/viewtopic.php?t=152855
[the right architecture for my system]:http://distfiles.gentoo.org/releases/amd64/current-iso/