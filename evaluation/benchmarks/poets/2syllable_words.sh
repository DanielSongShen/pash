# 2-syllable words
IN=${IN:-$PASH_TOP/evaluation/benchmarks/poets/input/pg/}
ls $IN | xargs cat | tr -sc '[A-Z][a-z]' ' [\012*]' | grep -i '^[^aeiou]*[aeiou][^aeiou]*[aeiou][^aeiou]$' | sort | uniq -c | sed 5q
