#!/bin/bash
/papyri/papyri.py --world $DATAFOLDER/backup/world --output $WEBFOLDER $2 2>&1 | tee $DATAFOLDER/logs/papyri.py.log
