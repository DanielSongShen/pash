#!/bin/bash

execute_seq_flag=0
eager_flag=0
no_task_par_eager_flag=0
auto_split_flag=0

while getopts 'senpa' opt; do
    case $opt in
        s) execute_seq_flag=1 ;;
        e) eager_flag=1 ;;
        n) no_task_par_eager_flag=1 ;;
        a) auto_split_flag=1 ;;
        *) echo 'Error in command line parsing' >&2
           exit 1
    esac
done
shift "$(( OPTIND - 1 ))"

## We assume that each evaluation script has a sequential, a
## distributed, and an environment
microbenchmark=$1
n_in=$2
results_subdir=$3
intermediary_prefix=$4

experiment="${microbenchmark}_${n_in}"

DISH_TOP=${DISH_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)}

eval_directory="../evaluation/"
directory="${eval_directory}/${4}intermediary/"
results="${eval_directory}results/${results_subdir}/"
prefix="${directory}${experiment}"
env_file="${prefix}_env.sh"
funs_file="${prefix}_funs.sh"
seq_script="${prefix}_seq.sh"
distr_script="${prefix}_distr.sh"

seq_output="${directory}/${microbenchmark}_seq_output"

echo "Environment:"
# cat $env_file
. $env_file
export $(cut -d= -f1 $env_file)

## Export necessary functions
if [ -f $funs_file ]; then
    source $funs_file
fi

if [ "$execute_seq_flag" -eq 1 ]; then
    echo "Sequential:"
    cat $seq_script
    { time /bin/bash $seq_script > $seq_output ; } 2> >(tee "${results}${experiment}_seq.time" >&2)
else
    echo "Not executing sequential..."
fi

## Save the configuration to restore it afterwards
auto_split_opt=""
config_path_opt=""

if [ "$auto_split_flag" -eq 1 ]; then
    echo "Distributed with auto-split:"
    eager_opt=""
    auto_split_opt="--split_fan_out ${n_in}"
    distr_result_filename="${results}${experiment}_distr_auto_split_fan_in_fan_out.time"
    ## TODO: Push this if-then-else in the outside script. Also make the split the default.
    # if [ "${microbenchmark}" != "bigrams" ] && [ "${microbenchmark}" != "spell" ] && [ "${microbenchmark}" != "double_sort" ] && [ "${microbenchmark}" != "max_temp_p123" ]; then
    #     echo "No reason to split on one-liner: ${microbenchmark}"
    #     exit
    # fi
elif [ "$eager_flag" -eq 1 ]; then
    echo "Distributed:"
    eager_opt=""
    distr_result_filename="${results}${experiment}_distr.time"
elif [ "$no_task_par_eager_flag" -eq 1 ]; then
    echo "Distributed with naive (no-task-par) eager:"
    eager_opt=""
    distr_result_filename="${results}${experiment}_distr_no_task_par_eager.time"

    ## Change the configuration
    config_path="/tmp/new-config.yaml"
    config_path_opt="--config_path ${config_path}"
    cat config.yaml > ${config_path}
    sed -i 's/tools\/eager/tools\/eager-no-task-par.sh/g' "${config_path}"
else
    echo "Distributed without eager:"
    eager_opt="--no_eager"
    distr_result_filename="${results}${experiment}_distr_no_eager.time"
fi

{ time python3.8 $DISH_TOP/compiler/dish.py --output_optimized $eager_opt $auto_split_opt $config_path_opt --output_time $seq_script $distr_script ; } 2> >(tee "${distr_result_filename}" >&2)

echo "Checking for equivalence..."
diff -s $seq_output /tmp/distr_output/0 | tee -a "${distr_result_filename}"

