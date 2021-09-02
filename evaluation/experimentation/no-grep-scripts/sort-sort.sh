IN=/home/daniel/Research/pash/evaluation/benchmarks/oneliners/input/10M.txt
cat $IN | tr A-Z a-z | sort | sort -r
