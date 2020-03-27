#!/bin/bash
/papyri/papyri.py --world $DATAFOLDER/backup/world --output $WEBDATA $1 2>&1 | tee -a $DATAFOLDER/logs/papyri.py.log
