#DATA_LIST=("1M.txt" "10M.txt" "100M.txt" "1G.txt")
DATA_LIST=("1M.txt" "10M.txt")
COMMAND_LIST=("grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4'" "grep '*'" "sort" "tr a-z A-Z" "wc" "uniq")
>&2 echo "${COMMAND_LIST[*]}"
CMD_NAME_LIST=("grep-complex" "grep-simple" "sort" "tr" "wc" "uniq")
>&2 echo "${CMD_NAME_LIST[*]}"
MAX_WIDTH=$(eval "nproc --all")
>&2 echo "$MAX_WIDTH"

for i in "${!COMMAND_LIST[@]}";
do
  # >&2 echo "$i"
  CMD_NAME="${COMMAND_LIST[$i]}"
  >&2 echo "${CMD_NAME_LIST[$i]}"
  for f in "${DATA_LIST[@]}";
  do
    DATA="$PASH_TOP/evaluation/benchmarks/oneliners/input/${f}"
    CMD="cat $DATA | $CMD_NAME"
    >&2 echo "$CMD"
    >&2 echo "$f"
    w=$MAX_WIDTH
    while [ "$w" -gt 0 ]
    do
      >&2 echo "w=$w"
      time for _ in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	    w=$(($w/2))
    done
  done
done

: '
CMD="cat $DATA | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4'"
>&2  echo "grep 100M"
>&2 echo "seq"
  time for i in {1..5}; do eval "$CMD"; done
w=2
while [ "$w" -lt 9 ]
do
  >&2 echo "w=$w"
  time for i in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	w=`expr $w + 2`
done

# DATA="$PASH_TOP/evaluation/tests/input/10M.txt"
# TODO evaluate on different input sizes
CMD="cat $DATA | sort"
>&2  echo "sort 100M"
>&2 echo "seq"
  time for i in {1..5}; do eval "$CMD"; done
w=2
while [ "$w" -lt 9 ]
do
  >&2 echo "w=$w"
  time for i in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	w=`expr $w + 2`
done

CMD="cat $DATA | tr a-z A-Z"
>&2  echo "tr 100M"
>&2 echo "seq"
  time for i in {1..5}; do eval "$CMD"; done
w=2
while [ "$w" -lt 9 ]
do
  >&2 echo "w=$w"
  time for i in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	w=`expr $w + 2`
done

CMD="cat $DATA | wc"
>&2  echo "wc 100M"
>&2 echo "seq"
  time for i in {1..5}; do eval "$CMD"; done
w=2
while [ "$w" -lt 9 ]
do
  >&2 echo "w=$w"
  time for i in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	w=`expr $w + 2`
done

CMD="cat $DATA | uniq"
>&2  echo "uniq 100M"
>&2 echo "seq"
  time for i in {1..5}; do eval "$CMD"; done
w=2
while [ "$w" -lt 9 ]
do
  >&2 echo "w=$w"
  time for i in {1..5}; do $PASH_TOP/pa.sh -w "$w" -c "$CMD"; done
	w=`expr $w + 2`
done
'