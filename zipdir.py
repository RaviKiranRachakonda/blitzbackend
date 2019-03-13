#!/usr/bin/env python
from __future__ import with_statement
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import os
 
def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[(len(basedir)+len(os.sep)-1):] #XXX: relative path
                z.write(absfn, zfn)
 
if __name__ == '__main__':
    import sys
    archivename = sys.argv[1]
    basedir = sys.argv[2]
    zipdir(basedir, archivename)

