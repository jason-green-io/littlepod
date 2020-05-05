#!/bin/bash
/papyri/papyri.py --world $DATAFOLDER/backup/world --output $WEBFOLDER $1 2>&1 | tee -a $DATAFOLDER/logs/papyri.py.log
