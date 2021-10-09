IN=/home/daniel/Research/pash/evaluation/benchmarks/oneliners/input/1M.txt
cat $IN | tr A-Z a-z | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4'
