### Generating a conditonal policy with AWScala 

One of the benefits of Amazon Web Services is the [IAM system]. This 
handy interface can be used to give people within, or outside, of your 
organization access to the console or content. Here's an example that 
is fairly common.

A tech-smart photographer takes his photo's with a high resolution 
camera and needs to deliver a few Gigabytes of data to a client. He has 
a few options: get a portalble hard-drive and hand the files over 
directly; upload the images to a private service and send the links to 
the client; or use something like dropbox to transfer the files over. 

Let's say the client isn't tech savvy enough to pull out the information 
from the hard-drives and they don't trust dropbox. So instead, the 
photographer tells them about his AWS S3 Bucket and provides a login for 
them to use. All good right? The client connects, navigates the S3 
interface like it was their usual file explorer, and downloads the images. 

But wait. What if the photographer has more than one client? How does he 
prevent one client from downloading another's work? After all, each client 
is only entitled to the work they've paid him for and no more. 

Enter [Policies]. 

Using a policy it's not too hard to restrict access to a single folder* 
inside of a bucket. Here's the gist of it: 

	{
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Sid": "AllowGroupToSeeBucketListAndAlsoAllowGetBucketLocationRequiredForListBucket",
	            "Action": [
	                "s3:ListAllMyBuckets",
	                "s3:GetBucketLocation"
	            ],
	            "Effect": "Allow",
	            "Resource": [
	                "arn:aws:s3:::*",
	                "arn:aws:s3:::my-bucket"
	            ]
	        },
	        {
	            "Sid": "AllowListBucketIfSpecificPrefixIsIncludedInRequest",
	            "Action": [
	                "s3:ListBucket"
	            ],
	            "Effect": "Allow",
	            "Resource": [
	                "arn:aws:s3:::my-bucket"
	            ],
	            "Condition" : {
	                "StringLike" : {
	                    "s3:prefix" : ["","ClientOne/*"]
	                }
	            }
	        },
	        {
	            "Sid": "AllowUserToReadObjectDataInClientsFolder",
	            "Action": [
	                "s3:GetObject"
	            ],
	            "Effect": "Allow",
	            "Resource": [
	                "arn:aws:s3:::my-bucket/ClientOne/*"
	            ]
	        },
	        {
	            "Sid": "ExplicitlyDenyAnyRequestsForAllOtherFoldersExceptForclients",
	            "Action": [
	                "s3:ListBucket"
	            ],
	            "Effect": "Deny",
	            "Resource": [
	                "arn:aws:s3:::my-bucket"
	            ],
	            "Condition": {
	                "StringNotLike": {
	                    "s3:prefix": [
	                        "",
	                        "ClientOne/*"
	                    ]
	                }
	            }
	        }
	    ]
	}

Ok, so maybe not the briefest things. But it's fairly clear what the 
policy does when you exam it. There are 4 statements. The first 2 
deal with access to the bucket and listing the contents. The third 
allows a user to download an object from the bucket. Last, the fourth 
denies access to any other bucket or folder if it doesn't match our 
specified folder.
 
While it's fun to write out the JSON by hand, or to use the [generator] 
that amazon provides. It's a bit faster to do this programmatically then 
it is to navigate all the screens inside the Amazon console. Using the 
[AWScala] library, we can create the same policy as above in code: 
	
	val sidName = "SomeNameYouWouldMake"
	val bucketName = "my-bucket"
	val keyToAllow = "ClientOne/" //
	val policy = Policy(
		Seq(
			Statement(Effect.Allow, 
				Seq(
					Action("s3:ListAllMyBuckets"), 
					Action("s3:GetBucketLocation")
				),
				Seq(
					Resource("arn:aws:s3:::*"),
					Resource(s"arn:aws:s3:::${bucketName}")
				),
				id = Some(s"AllowGroupToSeeBucketListAndAlsoAllowGetBucketLocationRequiredForListBucket${sidName}")
			),
			Statement(Effect.Allow,
				Seq(
					Action("s3:ListBucket")
				),
				Seq(
					Resource(s"arn:aws:s3:::${bucketName}")
				),
				id = Some(s"AllowListBucketIfSpecificPrefixIsIncludedInRequest${sidName}"),
				conditions = Seq(
					new awscala.Condition(							
						"s3:prefix",
						"StringLike",
						Seq("", s"${keyToAllow}*")
					)
				)
			),
			Statement(Effect.Allow, 
				Seq(
					Action(
						"s3:GetObject"
					)
				),
				Seq(
					Resource(
						s"arn:aws:s3:::${bucketName}/${keyToAllow}*"
					)
				),
				id = Some(s"AllowUserToReadObjectDataInFolderFor${sidName}")
			),
			Statement(Effect.Deny,
				Seq(
					Action(
						"s3:ListBucket"
					)
				),
				Seq(
					Resource(
						s"arn:aws:s3:::${bucketName}"
					)
				),
				id = Some(s"ExplicitlyDenyAnyRequestsForAllOtherFoldersExcept${sidName}"),
				conditions = Seq(
					new awscala.Condition(
						"s3:prefix",
						"StringNotLike",
						Seq("", s"${keyToAllow}*")
					)
				)
			)
		)
	)

You don't _have_ to set the `id` in the `Statement`s. But if you want 
them to mean something to you if you ever look into your group's policies 
then you should consider it. 

You may notice that the `Condition` is created using `new` unlike the 
other parts of the policy. This is doe to an [inconsitency that has since been fixed]. 
If you haven't tried out [AWScala], you should give it a try. The source 
code is clear enough most of the time that you can figure out how to do 
things quickly. The examples given in the [README] provide common use cases 
that should be good for most people. There's no conditional policy example, 
but you're welcome to use the one above as a starting point! 

[IAM system]:http://aws.amazon.com/iam/
[Policies]:http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html
[generator]:http://awspolicygen.s3.amazonaws.com/policygen.html
[AWScala]:https://github.com/seratch/AWScala
[inconsitency that has since been fixed]:https://github.com/seratch/AWScala/issues/83
[README]:https://github.com/seratch/AWScala/blob/master/README.md