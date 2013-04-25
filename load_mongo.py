#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import subprocess

subprocess.call('mongo edx --eval "db.dropDatabase()"', shell=True)
for f in os.listdir('.'):
    m = re.match('^(.*)\.mongo$', f)
    if m:
        collection = m.group(1)
        print collection
        subprocess.call('mongoimport --db edx --collection ' + collection + ' --file ' + collection + '.mongo', shell = True)
 