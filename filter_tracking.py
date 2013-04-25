#!/usr/bin/python
# Reads an edX click tracking file from a 7-Zip archive and filters
# the entries according to some criteria.
# Author: Derrick Coetzee, all rights waived under CC0.
import sys
import json
import os
from subprocess import *
if len(sys.argv) < 1 + 2:
    print('Syntax: ' + sys.argv[0] + ' <name of clicktracking 7z file> <max rows to write or -1 for all>')
    exit()
max_entries = int(sys.argv[2])
fnull = open(os.devnull, 'w')
proc = Popen('7z x -so "' + sys.argv[1] + '"', shell=True, stdout=PIPE, stderr=fnull)

entries_written = 0
while True:
    line = proc.stdout.readline()
    if len(line) == 0:
        break
    entry = json.loads(line.strip())
    if entry['username'] != '':
        for field in ['ip', 'agent']: # Don't care about these fields
            del entry[field]
        sys.stdout.write(json.dumps(entry) + "\n")
        entries_written += 1
        if entries_written == max_entries:
            sys.exit(0)
