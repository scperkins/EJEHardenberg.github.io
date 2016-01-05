from bs4 import BeautifulSoup
from hashlib import sha384
from base64 import encodestring

import json
with open('sri.conf') as f:
	conf = json.load(f)

#http://stackoverflow.com/a/19711609/1808164
def sha384OfFile(filepath):
    import hashlib
    sha = hashlib.sha384()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(2**10) # Magic number: one-megabyte blocks.
            if not block: break
            sha.update(block)
        return sha.digest() #modified from original so we return binary for encoding

def sriOfFile(filepath):
	sha = sha384OfFile(filepath)
	return encodestring(sha)[:-1] #drop newline added by b64

import os

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

searchLinks = []
searchScripts = []

for linkArray in conf['links']:
	sri = sriOfFile(linkArray[0])
	searchLinks.append( [linkArray[1] , sri])

for scriptArray in conf['scripts']:
	sri = sriOfFile(scriptArray[0])
	searchScripts.append( [scriptArray[1] , sri])

print searchLinks
print searchScripts

def isCssLink(tag):
	return tag.has_attr('rel') and 'stylesheet' in tag['rel']

allFiles = get_filepaths("www/")
for f in allFiles:
	if f.endswith(".html"):
		# Now open it up and update the SRI if neccesary
		data = ''
		with open(f,'r') as openedFile:
			soup = BeautifulSoup(openedFile, "lxml")
			links = soup.find_all(isCssLink)
			for link in links:
				for searchLink in searchLinks:
					if link['href'].endswith(searchLink[0]):
						link['integrity'] = searchLink[1]
			data = soup.prettify()
		with open(f, 'w') as openedFile:
			openedFile.write(data.encode('utf-8'))