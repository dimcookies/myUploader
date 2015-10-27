#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from sys import argv,exit
import re
import os
import flickrapi
import json
from xml.etree.ElementTree import tostring
from os import listdir
from os.path import isfile, join
from itertools import izip



props=open(os.path.dirname(os.path.realpath(__file__)) + "/properties").readlines()
API_KEY = props[0].strip()
API_SECRET = props[1].strip()

if len(argv) != 4:
	print "python ~/photo_list.py /tmp/directory Δίρφυ dirfi2014"
	print argv
	exit(-1)

def resize(params):
	#print params
	os.system("/usr/bin/convert " + params.encode("utf-8"))

flickr = None

def flickrAuthenticate():	
    print "Auth start"
    global flickr
    flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET)
    flickr.authenticate_via_browser(perms='write',format='json')
    print "Auth success"

def upload(fn):
    return "test"
    rsp = flickr.upload(filename=fn)
    #print tostring(rsp)
    status = rsp.attrib['stat'] #ok
    if status == 'ok':
        photoid = rsp.find('photoid').text
        p = flickr.photos.getInfo(photo_id=photoid, format='json')
        t = json.loads(p.decode('utf-8'))['photo']
        photo_url = "http://farm%s.staticflickr.com/%s/%s_%s_%s.%s" % (t['farm'], t['server'], t['id'], t['originalsecret'], 'o', t['originalformat'])
        return photo_url
    else:
        raise Exception(fn + " upload failed with response " + tostring(rsp))

def writeImageCacheFile(ar):
    urlFile = open("image_urls.txt","w")
    for i in ar:
        urlFile.write(i + "\n")
    urlFile.close()

def resizeImage(file, cnt, group, dirPath):
    #main image
    resize("\"" + join(dirPath,file)  + "\" -resize 1024\>" +  " " + group + str(cnt) + ".jpg")
    print "Image resize:" + group + str(cnt) + ".jpg"
    #thumbnail
    resize("\"" + join(dirPath,file)  + "\" -resize 350\>" +  " " + group + str(cnt) + "_t.jpg")
    print "Thumnail created:" + group + str(cnt) + "_t.jpg"

    return group + str(cnt) + ".jpg", group + str(cnt) + "_t.jpg"

template = u"""
<p>Ακολουθεί το δελτίο τύπου που εξέδωσε ο Ε.Ο.Σ. Χαλκίδας για την εξόρμηση %(title)s:</p>
<blockquote>
%(main)s
</blockquote>
<p><span style="line-height: 1.3em;">%(next)s Περισσότερες πληροφορίες Τρίτη &amp; Πέμπτη 18-21 μ.μ στα γραφεία του Συλλόγου Αγγελή Γοβιού 22. τηλ 2221025230</span></p>
<table style="width: 100%%;" border="0" cellspacing="15" cellpadding="15">
<tbody>
%(images)s
</tbody>
</table>
"""

two_images = """
<tr>
<td style="padding: 10px;"><a class="jcepopup" href="%s" target="_blank" rel="title[%s];caption[%s];group[%s]"> <img src="%s" border="0" alt="" title="" width="350" style="border-radius: 10px; border: 5px solid #fff; -webkit-transform: rotate(-2deg); -moz-transform: rotate(-2deg);" /> </a></td>
<td style="padding: 10px;"><a class="jcepopup" href="%s" target="_blank" rel="title[%s];caption[%s];group[%s]"> <img src="%s" border="0" alt="" title="" width="350" style="border-radius: 10px; border: 5px solid #fff; -webkit-transform: rotate(2deg); -moz-transform: rotate(2deg);" /> </a></td>
</tr>
"""

one_image = """<td style="padding: 10px;" %(extra_style)s><a class="jcepopup" href="%(img)s" target="_blank" rel="title[%(title)s];caption[%(title)s];group[%(group)s]"> <img src="%(thumb)s" border="0" alt="" title="" width="350" style="border-radius: 10px; border: 5px solid #fff; -webkit-transform: rotate(%(rot)sdeg); -moz-transform: rotate(%(rot)sdeg);" /> </a></td>"""

title = argv[2].decode('UTF-8')
group = unicode(argv[3])
dirPath = argv[1]

#unzip zip files
zips = filter(lambda f: isfile(join(dirPath,f)) and f.lower().find("zip") == (len(f)-3) ,listdir(dirPath))
for zipFile in zips:
 os.system("unzip " + zipFile)
# os.system("rm " + zipFile)

ar = []

#if images already been uploaded
if os.path.isfile("image_urls.txt"):
	urlFile = open("image_urls.txt")
	ar = filter(lambda x:x ,map(lambda l:l.strip(),urlFile.readlines()))
else:
	convFiles = []
	#get images and convert to utf8
	files = map(lambda file: file.decode("utf-8"), filter(lambda f: isfile(join(dirPath,f)) and f.lower().find("jpg") == (len(f)-3) ,listdir(dirPath)))
	files.sort()
	#print files
	cnt=0
	for file in files:
		cnt = cnt + 1
		print file
		#resize and add to upload list
		convFiles.extend(resizeImage(file, cnt, group, dirPath))

	if convFiles:
		#single authentication
		flickrAuthenticate()
		for i in convFiles:
				#upload image
				print "Uploading:"+i
				url = upload(i)
				print "Uploaded at url:" + url
				#add to cache file list
				ar.append(url)
				#remove resized image
				os.system("rm " + i)
		#write cache file				
		writeImageCacheFile(ar)

#docs = [ f for f in listdir(argv[1]) if (isfile(join(argv[1],f)) and (f.lower().find("doc") == (len(f)-3) or f.lower().find("docx") == (len(f)-4))) ]
docs = filter(lambda f: isfile(join(dirPath,f)) and (f.lower().find("doc") == (len(f)-3) or f.lower().find("docx") == (len(f)-4)) ,listdir(dirPath))
#print docs

#display doc for review, fix spelling mistakes
os.system("killall -9 oosplash")
os.system("killall -9 soffice.bin")
os.system("libreoffice \"" + join(dirPath,docs[0]) + "\"")

#no need since os.system is blocking
#response = raw_input("Continue (y/n): ")
#if response.lower() != 'y':
#	exit(-1)

#convert to text
os.system("killall -9 oosplash")
os.system("killall -9 soffice.bin")
os.system("libreoffice --norestore --headless --convert-to txt:Text \"" + join(dirPath,docs[0]) + "\"")

txtFile = docs[0].split(".")[0]+".txt"
f1=open(txtFile)

flag = False
content = []

for line in filter(lambda y:len(y) >0 , map(lambda x: x.strip(),f1.readlines())):
#	print line
	if flag:
		content.append(line)
		if line.find("www.eoschalkidas.gr") != -1:
			break
	else:
		if line.find("-"*10) != -1:
			flag = True		
		elif line.find("Ορειβατικού Συλλόγου Χαλκίδας") != -1:
			flag=True
			content.append(line)

print content[0]
print 
contentTitle = content[0].replace("Εξόρμηση του Ορειβατικού Συλλόγου Χαλκίδας","").strip().decode("UTF-8")
#next = content[-1].replace("Περισσότερες πληροφορίες Τρίτη & Πέμπτη 18-21 μ.μ στα γραφεία του Συλλόγου Αγγελή Γοβιού 22. τηλ 2221025230 και στην ιστοσελίδα. http://www.eoschalkidas.gr","").strip().decode("UTF-8")
next = re.sub(r'Περισσότερες πληροφορίες.*$','', content[-1]).strip().decode('UTF-8')
content = content[1:-1]

contentStr = "<br>".join(content).strip().decode("UTF-8")

os.system("rm \"" + txtFile+"\"");

#ar.sort()	
#print ar

def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

images = ""
single_image = ((len(ar)/2)%2  == 1)

cnt = 0
for img,thumb in pairwise(ar):
	if cnt%4 == 0:
		images = images + "<tr>\n"
	extra_style = ""	
	if single_image and cnt + 2 == len(ar):
		extra_style = 'colspan="2" align="center"'
	rot = "2"
	if cnt%4 == 0:
		rot = "-2"

	images = images + one_image % {"img" : img, "thumb":thumb, "title": title, "group":group, "extra_style":extra_style, "rot" : rot} + "\n"

	if cnt%4 == 2:
		images = images + "</tr>\n"	
	cnt = cnt + 2

if single_image:
		images = images + "</tr>\n"	


#print images
print template % {"title": contentTitle, "main": contentStr, "next":next, "images":images}
