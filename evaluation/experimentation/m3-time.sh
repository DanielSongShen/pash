#!/bin/bash
SCRIPT=$1
LOGFILE=$2
WIDTH=$3
exec 2>$LOGFILE
# echo "$SCRIPT"
echo "${PASH_TOP}/pa.sh -w $WIDTH $SCRIPT"
time for _ in {1..5}; do ${PASH_TOP}/pa.sh -w $WIDTH $SCRIPT; done