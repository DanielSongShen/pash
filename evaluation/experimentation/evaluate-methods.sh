#!/usr/bin/env bash
#DATA_FILE=$1
#>&2 echo $DATA_FILE
SCRIPT_LOC=$1
SCRIPT_LIST=("${SCRIPT_LOC}/"*)
# SCRIPT_LIST=("no-grep-scripts/no_grep.sh" "no-grep-scripts/testscript1.sh")
>&2 echo "${SCRIPT_LIST[*]}"
MAX_WIDTH=$(eval "nproc --all")
>&2 echo "$MAX_WIDTH"

for i in "${!SCRIPT_LIST[@]}";
do
  # >&2 echo "$i"
  SCRIPT_NAME="${SCRIPT_LIST[$i]}"
  >&2 echo "${SCRIPT_NAME}"
  M1_WIDTH=$(cat 'M1_widths.txt' | sed -n "${i+1} p")
  M2_WIDTH=$(cat 'M2_widths.txt' | sed -n "${i+1} p")
  M3_WIDTH=$(cat 'M3_widths.txt' | sed -n "${i+1} p")

  >&2 echo "M1 w=$M1_WIDTH"
  # >&2 echo "${PASH_TOP}/pa.sh -w $M1_WIDTH -c ./${SCRIPT_NAME} ${DATA_FILE}"
  time for _ in {1..5}; do "${PASH_TOP}"/pa.sh -w "$M1_WIDTH" "${SCRIPT_NAME}"; done
  >&2 echo "M2 w=$M2_WIDTH"
  time for _ in {1..5}; do "${PASH_TOP}"/pa.sh -w "$M2_WIDTH" "${SCRIPT_NAME}"; done
  >&2 echo "M3 w=$M3_WIDTH"
  time for _ in {1..5}; do "${PASH_TOP}"/pa.sh -w "$M3_WIDTH" "${SCRIPT_NAME}"; done

done
