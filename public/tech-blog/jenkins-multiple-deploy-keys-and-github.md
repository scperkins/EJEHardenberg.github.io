### Jenkins Multiple Deploy Keys and Github Hooks

The other day I ran into an annoying issue. And it's such common one that 
[github has a page for it]. I was setting up an application for continous 
integration. The common components were there. Application, [Jenkins],
and [a VCS], and there I was with an error. The issue is that you can't 
have a deploy key in use by multiple repositories. [Github suggests using machine users] 
but that's a bit of a pain in my opinion. As I rather manage everything 
from the server. 

#### Multiple SSH Keys and Jenkins

So the way around this is to setup a deploy key for each project. This 
is easily done with the command:

    ssh-keygen -t rsa -f <filename>

Since these are keys that will be used by machines, you'll want to leave 
the password  blank or you'll get some annoying issues to deal with later.
So, with that in mind become your jenkins user and create one!

    su jenkins #login as jenkins
    cd #change to jenkins's home directory
    ssh-keygen -t rsa -f .ssh/id_rsa_myreponame    

Next we'll do the "magic" here, open up your SSH configuration file like so
`vi .ssh/config` and enter:

    Host myrepo
      HostName github.com
      User git
      IdentityFile ~/.ssh/id_rsa_myreponame

Now that that's in place you can test the connection:

    ssh -T myrepo

And you'll get back the usual "You've successfully authenticated, but GitHub 
does not provide shell access." So you're halfway there. The next thing you 
should do is go to your Jenkins server, the job configuration you're working 
on, and update the github urls to use your new host. For example, if you're 
using the [Github Plugin for jenkins] you'll update the **Github project** area to
say: `myrepo/username/repository/. And if you're using the [Git plugin] you'll
update the **Source Code Management -> Repository URL** area to say: `myrepo/username/repo.git`
and set the **credentials** area to use the ssh file you just made. 

Once you do that and add the SSH key as a deploy key to github, you're done if you
just want to have the one jenkins server talk to multiple github projects. But wait,
there's more!

#### What about continous integration?

When it comes to the Github Jenkins Plugin, you're out of luck as far as I know. 
Because the `/github-plugin` hook, is sent the _Github version of the url_ in the
post data. You'll see nice errors like this in your logfile:

	INFO: Received POST for https://github.com/username/repo
	Aug 21, 2015 1:53:25 PM com.cloudbees.jenkins.GitHubRepositoryName create
	WARNING: Could not match URL myrepo:username/repo.git
	Aug 21, 2015 1:53:25 PM com.cloudbees.jenkins.GitHubWebHook processGitHubPayload
	INFO: Poked Specification Build

But, if you're using the git plugin you're in luck because the [push notification] 
takes a `url=` parameter that you can use to specify your customized url in. The 
useful thing (and I'm not sure if it's _supposed_ to do this, but it does) is this
endpoint responds to both GET and POST requests the same way. So you can go to your 
github repository settings and add a WebHook with the specified url:

	http://yourserver/git/notifyCommit?url=<URL of the Git repository>

To the Jenkins Hook URL field in the settings for the jenkins web hooks. And then you
should see builds when you push to your repository! 

[github has a page for it]:https://help.github.com/articles/error-key-already-in-use/
[Jenkins]:https://jenkins-ci.org/
[a VCS]:https://git-scm.com/
[Github suggests using machine users]:https://developer.github.com/guides/managing-deploy-keys/#machine-users
[Github Plugin for jenkins]:https://wiki.jenkins-ci.org/display/JENKINS/GitHub+Plugin
[Git plugin]:https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin
[push notification]:https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin#GitPlugin-Pushnotificationfromrepository

