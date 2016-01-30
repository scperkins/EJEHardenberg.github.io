deploy: push compile

push:
	git push origin master
	git push live master

compile: 
	harp compile
	git add .
	git commit -m "Compile Harp"

#Compure Subresource integrity hashes
sri:
	harp compile
	python sri.py
	git add .
	git commit -m "Compute SRI and Compile Harp"	
