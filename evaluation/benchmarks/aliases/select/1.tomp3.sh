#!/bin/bash

# tag: wav-to-mp3
set -e

IN=$PASH_TOP/evaluation/benchmarks/aliases/meta/wav
OUT=$PASH_TOP/evaluation/benchmarks/aliases/meta/out

find $IN -name '*.wav' | 
    xargs -n1 basename |
    sed "s;\(.*\);-i $IN/\1 -ab 192000 $OUT/\1.mp3;" |
    xargs -L1  ffmpeg