#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports edX forum MongoDB files into MongoDB database.

# Author: Derrick Coetzee, all rights waived under Creative Commons CC0 1.0
# (http://creativecommons.org/publicdomain/zero/1.0/).

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
 