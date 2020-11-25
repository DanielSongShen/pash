#!/bin/bash

microbenchmarks_dir="../evaluation/microbenchmarks/"
intermediary_dir="../evaluation/test_intermediary/"

echo "Deleting eager intermediate files..."
rm -f /tmp/eager*
mkdir -p $intermediary_dir
rm -rf "../evaluation/results/test_results/"
mkdir -p "../evaluation/results/test_results/"

n_inputs=(
    2
    8
)

microbenchmarks=(
    grep                 # PLDI
    minimal_sort         # PLDI
    minimal_grep         # PLDI
    topn                 # PLDI
    wf                   # PLDI
    spell                # PLDI
    shortest_scripts     # PLDI

    bigrams              # TODO: Fix bug. Run with good split.
    alt_bigrams          # Optimized version of Bigrams
    diff                 # TODO: Optimize diff
    set-diff             # TODO: Handle redirection after reduce

    sort                 # For comparison with sort --parallel

    ## Tests
    deadlock_test        # Test to check deadlock prevention using drain_stream
    double_sort          # Checks maximum peformance gains from split
    # for_loop_simple      # BUG: Output is not the same since it is overwritten
)

test_flags=(
    ""   # No split + No eager (This cannot be in the end)
    -n   # No split + Naive eager
)
#    -e   # No split + Eager
#    -a   # Split    + Eager


microbenchmark_configs=( )
for i in "${!microbenchmarks[@]}"; do
    all_flags=${test_flags[@]}
    microbenchmark_configs[$i]="${microbenchmarks[$i]};${all_flags// /;}"
done


## This is almost the same loop as the one in execute_evaluation_scripts
for microbenchmark_config in "${microbenchmark_configs[@]}"; do
    IFS=";" read -r -a flags <<< "${microbenchmark_config}"
    microbenchmark=${flags[0]}
    echo "Executing test: $microbenchmark"
    # Execute the sequential script on the first run only
    exec_seq="-s"
    for n_in in "${n_inputs[@]}"; do

        ## Generate the intermediary script
        python3 generate_microbenchmark_intermediary_scripts.py \
                $microbenchmarks_dir $microbenchmark $n_in $intermediary_dir "env_test"

        for flag in "${flags[@]:1}"; do
            echo "Flag: ${flag}"

            ## Execute the intermediary script
            ./execute_compile_evaluation_script.sh $exec_seq $flag "${microbenchmark}" "${n_in}" "test_results" "test_" #> /dev/null 2>&1
            rm -f /tmp/eager*

            ## Only run the sequential the first time around
            exec_seq=""
        done
    done
done

echo "Below follow the identical outputs:"
grep --files-with-match "are identical" ../evaluation/results/test_results/*_distr*.time

echo "Below follow the non-identical outputs:"
grep -L "are identical" ../evaluation/results/test_results/*_distr*.time
