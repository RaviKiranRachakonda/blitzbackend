#!/usr/bin/env python
import os
import shutil

def zipdir(basedir, archivename):
    shutil.make_archive(archivename, 'zip', basedir)

if __name__ == '__main__':
    import sys
    archivename = sys.argv[1]
    basedir = sys.argv[2]
    zipdir(basedir, archivename)

