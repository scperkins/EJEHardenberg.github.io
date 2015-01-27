### Mutt, Vim, and a win! 

Today, [after dealing with a segfault], I started playing with [mutt] and
so far I'm really liking it. For example, if you have a gmail account 
there exists [a LOT] of different [tutorials] on the web about connecting,
and if you use another service, there's a high chance that google or [duckduckgo] 
will find it for you. So I won't be covering how to connect mutt to servers
in this post. Instead, I'd like to explain why I picked up mutt in the first place. 
And a useful trick for you if you use vim as your editor of choice.


When I send [pgp] encrypted emails, I have to do something like the 
following:

1. Open vim
2. write message
3. open terminal (not hard, I have quake so it's just one button)
4. `cat file | gpg --encrypt --armor -r <recipient>`
5. copy output
6. open email client
7. paste pgp message
8. enter recipients for message
9. send

That's **9** steps to do something that should be simple! 

Well, after installing and configuring mutt I can now skip the last 4
steps, which means now I'm left with the other 5. Since mutt will handle
opening vim for us, we'll actually end up with 4 steps.

1. start mutt
2. compose message
3. ???
4. send

The magical _???_ is what we'll explore next. I was trying to figure out
how I could send whatever was in my txt file to gpg when I happened upon
[this page] and found this useful note:

<blockquote>
    In visual mode, just highlight the text you want to work with, then run :! commandname .
</blockquote>

So if I'm in visual mode I can simply type my gpg encryption command and 
the message will get automatically replaced with the encrypted text. This
is all good and great, but the only part of the command that changes is 
the recipients. So writing the `--encrypt --armor` all the time is a bit
redundant to me, and [programmers are lazy], so I decided to finally look
up how to write a vim macro.

Perhaps the strangest thing while writing the macro was trying to determine
how to STOP recording while still in the middle of a command in vim. Sadly, I didn't
figure it out (I'm sure I'm missing a manual somewhere), but I did figure 
out a way to remove the esc + q keys I had to press to get out of it. Which 
is essentially the same thing. Doing this let's us fill in the other options
we want to pass to gpg.

In order to do this yourself follow these steps:

1. open anything up in vim, or make a new file and write make a few lines of text.
2. press `q` then `e` to begin recording a macro into the e register.
3. press `:0` to jump to the top of the file
4. type `shift+v` to enter visual mode
5. type `shift+g` to jump to the bottom of the file
6. type `:!gpg --encrypt --armor -r `
7. press `ESC`, then `q` then `e` to finish recording
8. Next, enter command mode and type `let @e='` then press `Ctrl+r Ctrl+r e`
9. This should paste the full register into the space, and you'll notice some trailing mess at the end like `^]`
10. Delete said mess, leaving a space after `-r` and put in the last apostrophe and hit enter.
11. you can now press `@e` at any time to open up the prompt to enter recipients and encrypt the whole file.

Or, the TL;DR version, add this to your _.vimrc_ file:

	let @e=':0^MVG:!gpg --encrypt --armor -r '

Note that when you enter the ^M, you'll want to use `Ctrl+v` then press the enter
key otherwise the command will **not** work!

So now we have a method to easily encrypt the body of an email message. What about
decrypting? If you'd like to record this one yourself, you can do the following 
steps or skip down to the _.vimrc_ command:

1. press `q` then `d` to start recording into the d register
1. `/-----BEGIN PGP MESSAGE`
2. `shift + v` to enter visual mode
3. `/END PGP MESSAGE-----`
4. `:!gpg --decrypt ` his enter to decrypt, then `ESC` and `d` to end the recording

All in all, add this to the _.vimrc_ file

    let @d='/-----BEGIN PGP MESSAGE^MV/END PGP MESSAGE-----^M:!gpg --decrypt^M'

again, making sure to use `ctrl+v` then the enter key to add the `^M` parts.

Now you can encrypt and decrypt extremely easily! If you're interested in reading
more about vim's commands, I'd recommend the [documentation]. It's quite easy to 
follow, and if you want to know specifically about macros, you should read the 
[wiki] page on it, it's got a lot of good information.




[after dealing with a segfault]:http://www.ethanjoachimeldridge.info/tech-blog/apt-get-segfault-mutt
[mutt]:http://www.mutt.org/
[a LOT]:http://askubuntu.com/questions/122480/how-to-manage-multiple-imap-accounts-with-mutt
[tutorials]:https://www.bartbania.com/raspberry_pi/consolify-your-gmail-with-mutt/
[cock.li]:cock.li
[pgp]:http://www.pgpi.org/
[this page]:http://www.softpanorama.org/Editors/Vimorama/vim_running_external_commands.shtml
[programmers are lazy]:http://blogoscoped.com/archive/2005-08-24-n14.html
[documentation]:http://vimdoc.sourceforge.net/htmldoc/map.html
[wiki]:http://vim.wikia.com/wiki/Macros
[duckduckgo]:https://duckduckgo.com/