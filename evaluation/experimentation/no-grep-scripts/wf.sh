IN=/home/daniel/Research/pash/evaluation/benchmarks/oneliners/input/10M.txt
cat $IN | tr -cs A-Za-z '\n' | tr A-Z a-z | sort | uniq -c | sort -rn
