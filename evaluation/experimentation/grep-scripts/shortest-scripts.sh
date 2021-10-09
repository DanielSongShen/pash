IN=/home/daniel/Research/pash/evaluation/benchmarks/oneliners/input/1M.txt
cat $IN | xargs file | grep "shell script" | cut -d: -f1 | xargs -L 1 wc -l | grep -v '^0$' | sort -n | head -15