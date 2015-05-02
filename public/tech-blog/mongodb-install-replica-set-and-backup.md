### Installing a MongoDB replica set and backup script

While I generally stick to Relational databases such as mySQL, there 
are times when you really only need a document store and the right tool 
for the job is something else. In this case, I needed to install and 
configure a mac machine for a development environment that replicated 
the production one. A small replica set of 3 nodes all running MongoDB. 

In addition to installation and configuring, it's also prudent to set up 
how to backup and restore your data. So this post will cover that as 
well:

#### Installing MongoDB on Mac

First off, we have to download mongodb:
	
	curl -O http://downloads.mongodb.org/osx/mongodb-osx-x86_64-3.0.2.tgz

And being security conscious, we'll check that the download is valid 
by computing it's SHA hashes:

	curl -LO http://downloads.mongodb.org/osx/mongodb-osx-x86_64-3.0.2.tgz.sha1
	curl -LO http://downloads.mongodb.org/osx/mongodb-osx-x86_64-3.0.2.tgz.sha256

	shasum mongodb-osx-x86_64-3.0.2.tgz
	9018f01e80eef7428f57ad23cf1e8bcbeea6b472  mongodb-osx-x86_64-3.0.2.tgz

	cat mongodb-osx-x86_64-3.0.2.tgz.sha1 
	9018f01e80eef7428f57ad23cf1e8bcbeea6b472  mongodb-osx-x86_64-3.0.2.tgz 

	shasum -a 256 mongodb-osx-x86_64-3.0.2.tgz
	6d435f66cc25a888ab263be27106abe7ef8067189199869f3e7e8126757f5286  mongodb-osx-x86_64-3.0.2.tgz

	cat mongodb-osx-x86_64-3.0.2.tgz.sha256 
	6d435f66cc25a888ab263be27106abe7ef8067189199869f3e7e8126757f5286  mongodb-osx-x86_64-3.0.2.tgz

Convinced in the authenticity of the files we can move onto installing:

	tar -zxvf mongodb-osx-x86_64-3.0.2.tgz
	mkdir /opt/local/mongodb
	sudo cp -R -n mongodb-osx-x86_64-3.0.2/ /opt/local/mongodb
	echo 'export PATH=/opt/local/mongodb/bin:$PATH' >> ~/.profile
	source ~/.profile
	mkdir -p /opt/local/mongodb/data/db

At this point you're almost ready, you just need to set the permissions 
correctly. Namely that whoever is starting the mongo process can read 
and write to the data directory. 

	sudo chown -R user:group /opt/local/mongodb

And now it will run when you run mongo via the mongod command:

	mongod --dbpath /opt/local/mongodb/data/db

#### Setting up a local Replica Set

With the basics done and ready, we can now configure and create a 3 
node replica set. Mongodb's website provides [documentation on this] 
but for completeness, I'll reproduce it here specifically to the setup 
described above:

First, the data directories for each replica:

	mkdir -p /opt/local/mongodb/data/srv/mongodb/rs0-{0,1,2}

Next, we'll make it easier to start up our local cluster:

	osascript -e 'tell app "Terminal"
    	do script "mongod --port 27017 --dbpath /opt/local/mongodb/data/srv/mongodb/rs0-0 --replSet rs0 --smallfiles --oplogSize 128"
    	do script "mongod --port 27018 --dbpath /opt/local/mongodb/data/srv/mongodb/rs0-1 --replSet rs0 --smallfiles --oplogSize 128"
    	do script "mongod --port 27019 --dbpath /opt/local/mongodb/data/srv/mongodb/rs0-2 --replSet rs0 --smallfiles --oplogSize 128"
	end tell'

Place this code into a script, called: 'startmongo.sh' and `chmod +x` 
the file. Run it from your command line `./startmongo.sh` and you'll 
see three windows appear, each running an instance of mongod.

The arguments to each mongod instance are pretty regular, the only 
ones which may be out of the ordinary are `--smallfiles` and 
`--oplogSize`, which the documentation says:

>The --smallfiles and --oplogSize settings reduce the disk space that each mongod instance uses. This is ideal for testing and development deployments as it prevents overloading your machine. For more information on these and other configuration options, see Configuration File Options.

Running 3 instances of mongo does not give us a replica set quite yet. 
We need to tell the servers to _be_ one first, so connect to one of 
them:

	mongo --port 27017

Then create the configuration object:

	rsconf = {
           _id: "rs0",
           members: [
                      {
                       _id: 0,
                       host: "localhost:27017"
                      }
                    ]
         }
    rs.initiate(rsconf)
    rs.add("localhost:27018")
    rs.add("localhost:27019")
    rs.status()

and the last command should display something like so:

	{
		"set" : "rs0",
		"date" : ISODate("2015-05-01T17:26:11.546Z"),
		"myState" : 1,
		"members" : [
			{
				"_id" : 0,
				"name" : "localhost:27017",
				"health" : 1,
				"state" : 1,
				"stateStr" : "PRIMARY",
				"uptime" : 4607,
				"optime" : Timestamp(1430501157, 1),
				"optimeDate" : ISODate("2015-05-01T17:25:57Z"),
				"electionTime" : Timestamp(1430501100, 2),
				"electionDate" : ISODate("2015-05-01T17:25:00Z"),
				"configVersion" : 3,
				"self" : true
			},
			{
				"_id" : 1,
				"name" : "localhost:27018",
				"health" : 1,
				"state" : 2,
				"stateStr" : "SECONDARY",
				"uptime" : 18,
				"optime" : Timestamp(1430501157, 1),
				"optimeDate" : ISODate("2015-05-01T17:25:57Z"),
				"lastHeartbeat" : ISODate("2015-05-01T17:26:09.903Z"),
				"lastHeartbeatRecv" : ISODate("2015-05-01T17:26:11.430Z"),
				"pingMs" : 0,
				"lastHeartbeatMessage" : "could not find member to sync from",
				"configVersion" : 3
			},
			{
				"_id" : 2,
				"name" : "localhost:27019",
				"health" : 1,
				"state" : 2,
				"stateStr" : "SECONDARY",
				"uptime" : 13,
				"optime" : Timestamp(1430501157, 1),
				"optimeDate" : ISODate("2015-05-01T17:25:57Z"),
				"lastHeartbeat" : ISODate("2015-05-01T17:26:09.903Z"),
				"lastHeartbeatRecv" : ISODate("2015-05-01T17:26:10.027Z"),
				"pingMs" : 0,
				"configVersion" : 3
			}
		],
		"ok" : 1
	}


#### Backing up your data

First we'll make a little bit of test data. From within the mongo 
console you're running:

	use site
	db.Site.insert( { page: "home", "url" : "/" } )
	db.Site.insert( { page: "contact" , url : "/contact"})

We _could_ use the `mongodump` and `mongorestore` tools to do out 
backup. But, these tools take a while if you've got a lot of data. 
While in our example we obviously don't, an example is only as useful 
as it is scalable. Plus, the two tools don't lock the writes to the 
database, and therefore during the long period of time a backup or 
restore can take, the data may become inconsistent with the snapshot 
we're taking. 

Since that's somewhat counter to the point of making a backup. We'll 
elect a file system snapshot instead. First we'll lock the database 
from writes:

	db.fsyncLock()

Once the database is locked, you can perform a snapshot of the data 
directory itself easily:

	cd /opt/local/mongodb/
	tar -czf data.bak.tar.gz data

Note that the back up will have a `mongod.lock` file in each directory 
so you'll have to remove that before you restore from the backup.  

Once you've saved a copy of the data directory you can unlock the database:

	db.fsyncUnlock()

This does have some caveats of course. When done on a local machine 
such as what we've configured, it's easy to get a snapshot of each 
replica all in one go. On an actual production setup, each instance 
would likely be on a different server. So you'd need to `ssh` to the 
servers. To determine which node is the primary you can ask any of the 
servers:

	db.serverStatus().repl.primary

Then go from there. Here's a full cli session pretending to have a 
hemoraging database:

	# start up the mongo cluster
	./start-mongodb.sh

	# 3 terminals should appear and we'll see our data if we ask for it:
	mongo --port 27017
	use site
	db.Site.find()
	{ "_id" : ObjectId("5543b9ac53eeee01a167b662"), "page" : "home", "url" : "/" }
	{ "_id" : ObjectId("5543c6ea53eeee01a167b663"), "page" : "contact", "url" : "/contact" }
	
	# Now we backup our data:
	db.fsyncLock()
	{
		"info" : "now locked against writes, use db.fsyncUnlock() to unlock",
		"seeAlso" : "http://dochub.mongodb.org/core/fsynccommand",
		"ok" : 1
	}

	exit
	cd /opt/local/mongodb
	tar -czf data.bak.tar.gz data

	# Now we connect to mongo and let it go continue:

	mongo --port 27017
	db.fsyncUnlock()
	{ "ok" : 1, "info" : "unlock completed" }
	
	# And now let's screw up our data and such
	exit
	mv data data.corrupt
	killall mongod # you will see errors here

	# Pretend we noticed mongo was down and decided to restart it:
	./start-mongodb.sh

	# Oh no we have bad data! Guess we need to restore out data!
	Shutdown each mongo cluster

	killall mongodb

	# or use service mongo stop or what have you. Then, restore:

	tar -xzf data.bak.tar.gz 

	# remove the lock files
	rm data/srv/mongodb/rs0-0/mongod.lock 

	# start mongo services
	./start-mongodb.sh

	mongo --port 27017
	use site
	db.Site.find()
	{ "_id" : ObjectId("55453e54eb69b58f76c761f7"), "page" : "home", "url" : "/" }
	{ "_id" : ObjectId("55453e66eb69b58f76c761f8"), "page" : "contact", "url" : "/contact" }

	# Phew we're safe!

In general, snapshotting the file system is the safest and best way to 
preserve all your data. Using the mongo dump and restore tools is ok if 
you don't have much data, or if your data isn't complex enough to need 
its entire BSON data saved. The best part is you can take the zipped 
files and save them to a backup server for safety or local use!


[documentation on this]:http://docs.mongodb.org/manual/tutorial/deploy-replica-set-for-testing/