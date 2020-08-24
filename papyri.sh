#!/bin/bash
/papyri/papyri.py --world $DATAFOLDER/backup/world --output $WEBFOLDER --type $TYPE $2 2>&1 | tee $DATAFOLDER/logs/papyri.py.log
