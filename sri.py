from bs4 import BeautifulSoup

import json

with open('sri.conf') as f:
	conf = json.load(f)

for link in conf['links']:
	print link

for script in conf['scripts']:
	print script
