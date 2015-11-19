### Connect Visual VM to a docker container

In order to connect Visual VM to Docker you need to open the ports 
between the host and the container as well as specify the jmxremote
port because the container, from the local perspective, is a remote 
JVM. You need to start java with a few extra parameters, so your 
Dockerfile might end with something like this:


	ENTRYPOINT ["java -jar", "myjar.jar" "-Dcom.sun.management.jmxremote.port=<port>","-Dcom.sun.management.jmxremote.authenticate=false","-Dcom.sun.management.jmxremote.ssl=false","-Dcom.sun.management.jmxremote.rmi.port=<port>","-Djava.rmi.server.hostname=<docker ip>"]

Where `<port>` is something like 8000 throughout, and the `<docker ip>` 
is the IP address that you can get from your boot2docker or docker machine
configuration. If you're using docker machine you can use: 

	docker-machine ls # find your machine name
	docker-machine env <machine name>

Then you want to run your container with the port open and specified: 

	docker run -p 80:80 --expose <port> -p <port>:<port> t test 

And then in VisualVM you can click "Add JMX Connection" and specify 
the same `<docker ip`> and the port you've opened. Once you've done 
that you should have the connection open. If you perform heap dumps 
you'll need to copy the file from the docker container. You can copy 
a file from docker like so:

	docker ps #get your container id
	docker cp <container id>:/tmp/heapdump-1447875373977.hprof ~/Desktop/dump

Don't forget to copy the filename that VisualVM tells you when you 
click heap dump.
