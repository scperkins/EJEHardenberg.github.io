deploy: sri push

push:
	git push origin master
	git push live master

#Compure Subresource integrity hashes
sri:
	harp compile
	python sri.py
	git add .
	git commit -m "Compute SRI and Compile Harp"	
