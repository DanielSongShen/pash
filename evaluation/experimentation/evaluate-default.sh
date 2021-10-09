#!/usr/bin/env bash
SCRIPT_LOC=$1
SCRIPT_LIST=("${SCRIPT_LOC}/"*)

for i in "${!SCRIPT_LIST[@]}";
do
  # >&2 echo "$i"
  SCRIPT_NAME="${SCRIPT_LIST[$i]}"
  >&2 echo "${SCRIPT_NAME}"
  >&2 echo "W=2"
  # >&2 echo "${PASH_TOP}/pa.sh -w $M1_WIDTH -c ./${SCRIPT_NAME} ${DATA_FILE}"
  time for _ in {1..5}; do "${PASH_TOP}"/pa.sh "${SCRIPT_NAME}"; done
done