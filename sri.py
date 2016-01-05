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
	return encodestring(sha)

for linkArray in conf['links']:
	sri = sriOfFile(linkArray[0])
	print sri

for scriptArray in conf['scripts']:
	sri = sriOfFile(scriptArray[0])
	print sri
