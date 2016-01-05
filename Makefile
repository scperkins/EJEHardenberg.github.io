deploy:
	harp compile
	git add .
	git commit -m "Compile Harp"
	git push origin master
	git push live master
