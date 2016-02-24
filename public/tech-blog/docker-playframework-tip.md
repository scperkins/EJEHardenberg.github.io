### Tip for dockerized Play! Framework applications

If your application is continously restarting and you're running in a
dockerized environment there's probably one simple (and obnoxious)
reaason why. The long and short of it is that whether you use
`ENTRYPOINT` or `CMD` to start your application, you need to set play's
pid file to something that's transient. Like so:

	-Dpidfile.path=/var/run/play.pid

or

	-Dpidfile.path=/dev/null

You might wonder why this is neccesary if you've dockerized your
container. The answer is pretty easy to understand through an example.
First, create a docker container that installs whatever version of Java
you need. Second run `sbt dist` or use an [assembly plugin] to create your
executable. Last, create a Dockerfile that uses the java version and
adds the neccesary files for your executable to itself, then runs the
application.

The next thing to do is to build and run your docker container. While
it's running, open up another terminal and issue the commands:

	docker ps # Grab the container Id of your running image
	docker kill -s=9 <container id>
	docker start <container id>

Wait a moment, then run `docker logs <container id>` and observe the
application refusing to boot because:

	Play server process ID is 1
	This application is already running (Or delete RUNNING_PID file).

which happens because in the event that a docker container quits
unexpectantly it has the following behavior:

>By default a container’s file system persists even after the container
>exits. This makes debugging a lot easier (since you can inspect the
>final state) and you retain all your data by default. 

Which is a [quote from the docs]. So when your play application is
running and the container quits suddenly, play doesn't clean up after
itself and you end up with a PID file that causes play to think it's
already running. If you update your code to set the pid file to
somewhere temporary, or to send it to `/dev/null` (do this if play's the
only thing running in the container) then you won't have this issue. 

Hope that helps someone out there who didn't [RTFM]

[quote from the docs]:https://docs.docker.com/engine/reference/run/#clean-up-rm
[assembly plugin]:https://github.com/sbt/sbt-assembly
[RTFM]:https://www.playframework.com/documentation/2.3.x/ProductionConfiguration#Changing-the-path-of-RUNNING_PID
