#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import shutil
from nameparser import HumanName
from string import Template
import datetime
import os
import subprocess
from xml.sax.saxutils import escape

from itertools import zip_longest
import re

#UPDATE VALUES

#filename of volume pdfs
volumeonefilename = 'ICLS 2014 Volume 1 (PDF)-wCover.pdf'
volumetwofilename = 'ICLS 2014 Volume 2 (PDF)-wCover.pdf'
volumethreefilename = 'ICLS 2014 Volume 3 (PDF)-wCover.pdf'

#first page of first paper in the volume
volumeonestart = 23
volumetwostart = 625
volumethreestart = 1179

#pdf page number minus written page number
volumeonepageoffset = 40
volumetwopageoffset = -582
volumethreepageoffset = -1136

#first page of last paper of last volume
startoflastpaper = 1763

#page after last page of last paper of last volume
endofdoc = 1764 

subj = Template(u'<dc:subject xml:lang="en">$subject</dc:subject>')
def subjects(sstr):
    s = sstr.split(',')
    return "\n".join([escape(subj.substitute(subject=x.strip())) for x in s])
def genDatetime():
    return datetime.datetime.now().isoformat()[0:19] + 'Z'

author = Template(u'<dcvalue element="contributor" qualifier="author">$author</dcvalue>')
def makeAuthors(authors):
    return "\n".join([author.substitute(author=y.last + ", " + (y.first + ' ' + y.middle).strip()) for y in [HumanName(x) for x in names]])

def makeAuthorCit(name):
    y = HumanName(name)
    if name == '' or y.first == '':
        return ''
    init = y.first[0] + '.'
    if y.middle != '':
        init = init + ' ' + y.middle[0] + '.'
    return y.last + ", " + init

def makeAuthorsCit(ys):
    if len(ys) == 1:
        return makeAuthorCit(ys[0])
    if len(ys) == 2:
        return escape(makeAuthorCit(ys[0]) + " & " + makeAuthorCit(ys[1]))
    start =  ", ".join([makeAuthorCit(y) for y in ys[:-1]]).strip()
    return escape(start + ", & " + makeAuthorCit(ys[-1:][0]))

item = Template(u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
    <dublin_core schema="dc">
    $authors
      <dcvalue element="date" qualifier="accessioned">$datetime</dcvalue>
      <dcvalue element="date" qualifier="available">$datetime</dcvalue>
      <dcvalue element="date" qualifier="issued">2014-06</dcvalue>
      <dcvalue element="identifier" qualifier="citation" language="en_US">$authorscit&#x20;(2014).&#x20;$title.&#x20;In&#x20;Joseph&#x20;L.&#x20;Polman,&#x20;Eleni&#x20;A.&#x20;Kyza,&#x20;D.&#x20;Kevin&#x20;O'Neill,&#x20;Iris&#x20;Tabak,&#x20;William&#x20;R.&#x20;Penuel,&#x20;A.&#x20;Susan&#x20;Jurow,&#x20;Kevin&#x20;O'Connor,&#x20;Tiffany&#x20;Lee,&#x20;and&#x20;Laura&#x20;D'Amico&#x20;(Eds.).&#x20;Learning&#x20;and&#x20;Becoming&#x20;in&#x20;Practice:&#x20;The&#x20;International&#x20;Conference&#x20;of&#x20;the&#x20;Learning&#x20;Sciences&#x20;(ICLS)&#x20;2014.&#x20;$volume.&#x20;Colorado,&#x20;CO:&#x20;International&#x20;Society&#x20;of&#x20;the&#x20;Learning&#x20;Sciences,&#x20;pp.&#x20;$pages.</dcvalue>
      <dcvalue element="identifier" qualifier="uri">https://doi.dx.org&#x2F;10.22318&#x2F;icls2014.$id</dcvalue>
      <dcvalue element="description" qualifier="abstract" language="en_US">$abstract</dcvalue>
      <dcvalue element="language" qualifier="iso" language="en_US">en</dcvalue>
      <dcvalue element="publisher" qualifier="none" language="en_US">Boulder, CO:&#x20;International&#x20;Society&#x20;of&#x20;the&#x20;Learning&#x20;Sciences</dcvalue>
      <dcvalue element="title" qualifier="none" language="en_US">$title</dcvalue>
      <dcvalue element="type" qualifier="none" language="en_US">Book&#x20;chapter</dcvalue>
    </dublin_core>
""")

f = open('newtoc', 'r').read().strip().split('\n')

g  =list(zip(*[iter(f)]*2))

cs = []
for group in g:
    line = group[0].replace("\r", "").strip()
    fline = re.match(r"(.+?) *\.+? *(\d+?)$", line)
    title = fline.groups(1)[0].strip()
    page = fline.groups(1)[1].strip()
    authors = group[1].replace("\r", "").strip()
    if int(page) >= volumeonestart and int(page) < volumetwostart:
        volume = 'Volume 1'
    elif int(page) >= volumetwostart and int(page) < volumethreestart:
        volume = 'Volume 2'
    elif int(page) >= volumethreestart and int(page) < endofdoc:
        volume = 'Volume 3'
    else:
        raise ValueError("Page number is outside of the provided range", int(page), volumeonestart, endofdoc)

    cs.append([int(page),title,authors, volume])

print(cs)

for idx, c in enumerate(cs):
    startpage = c[0]
    if startpage == startoflastpaper:
        endpage = endofdoc
    else:
        endpage = cs[idx+1][0]
    print("Processing " + str(startpage) + " - " + str(endpage-1) + " pages and volume " + str(c[3]))
    if c[3] == 'Volume 1':
        fin = subprocess.run(['/bin/bash', './split.sh', volumeonefilename, str(startpage+volumeonepageoffset), str(endpage+volumeonepageoffset-1),'pdfs/' + str(startpage) + '-' + str(endpage-1) + '.pdf'])
 
    if c[3] == 'Volume 2':
        fin = subprocess.run(['/bin/bash', './split.sh', volumetwofilename, str(startpage+volumetwopageoffset), str(endpage+volumetwopageoffset-1),'pdfs/' + str(startpage) + '-' + str(endpage-1) + '.pdf'])
       
    if c[3] == 'Volume 3':
         fin = subprocess.run(['/bin/bash', './split.sh', volumethreefilename, str(startpage+volumethreepageoffset), str(endpage+volumethreepageoffset-1),'pdfs/' + str(startpage) + '-' + str(endpage-1) + '.pdf'])
   # if startpage == 206:
    fin = subprocess.run(['pdftotext', '-simple', 'pdfs/'+ str(startpage)+'-'+ str(endpage-1)+'.pdf'])
    ff = open('pdfs/'+ str(startpage)+"-"+ str(endpage-1)+'.txt', 'rb').read().decode('utf8', 'ignore').strip().replace('\n','ZZZZ')

    match = re.match(r".*Abstract[:.](.+?)ZZZZZZZZ", ff, re.MULTILINE)
    if match:
        abstract = escape(' '.join(match.groups(1)[0].replace('ZZZZ', ' ').split()))
    else:
        abstract = ''
    names = c[2].split(',')
    authorscit = makeAuthorsCit(names)
    authors = makeAuthors(names)
    id = str(startpage)+'-'+str(endpage-1)
    full = item.substitute(authors=authors, authorscit=authorscit, title=escape(c[1]), datetime=genDatetime(),id=str(startpage), abstract=escape(abstract), volume=escape(c[3]),pages=str(startpage)+'-'+str(endpage-1))
    #print(full)
    # dir = 'import/' + id
    # try:
    #     os.mkdir(dir)
    # except:
    #     pass
    # xmlf = open(dir + '/dublin_core.xml', 'w')
    # xmlf.write(full)
    # open(dir + '/contents', 'w').write(id + '.pdf')
    # shutil.copyfile('pdfs/'+ id + '.pdf', dir+'/'+id+'.pdf')



    # if startpage == 1763:
    #     break
