# verses with 2 or more, 3 or more, exactly 2 instances of light.
INPUT=${INPUT:-$PATH_TOP/evaluation/scripts/input/genesis}
grep -c 'light.*light' ${INPUT} 
grep -c 'light.*light.*light' ${INPUT}
grep 'light.*light' ${INPUT} | grep -vc 'light.*light.*light' 