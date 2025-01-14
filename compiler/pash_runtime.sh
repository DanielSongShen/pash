#!/bin/bash

##
## High level design. 
##
## (1) The `pash_runtime` should behave as a wrapper, saving all the necessary state:
##     - previous exit code
##     - previous set status
##     - previous variables
##     and then reverting to PaSh internal state
##
## (2) Then it should perform pash-internal work.
##
## (3) Then it should make sure to revert the exit code and `set` state to the saved values.
##
## (4) Then it should execute the inside script (either original or parallel)
##     TODO: Figure out what could be different before (1), during (4), and after (7) 
##
## (5) Then it save all necessary state and revert to pash-internal state. 
##     (At the moment this happens automatically because the script is ran in a subshell.)
##
## (6) Then it should do all left pash internal work.
##
## (7) Before exiting it should revert all exit state.
##
## Visually:
##
## -- bash -- | -- pash --
##    ...     |
##      \----(1)----\
##            |     ...
##            |     (2)
##            |     ...
##      /----(3)----/
##    ...     |
##    (4)     |
##    ...     |
##
## (The rest of the steps happen only in debug mode)
##    ...
##      \----(5)----\
##            |     ...
##            |     (6)
##            |     ...
##      /----(7)----/
##    ...     |

## TODO: Make a list/properly define what needs to be saved at (1), (3), (5), (7)
##
## Necessary for pash:
## - PATH important for PaSh but might be changed in bash
## - IFS has to be kept default for PaSh to work
##
## Necessary for bash:
## - Last PID $! (TODO)
## - Last exit code $?
## - set state $-
## - File descriptors (TODO)
## - Loop state (?) Maybe `source` is adequate for this (TODO)
## - Traos (TODO)
##
## (maybe) TODO: After that, maybe we can create cleaner functions for (1), (3), (5), (7). 
##               E.g. we can have a correspondence between variable names and revert them using them 

##
## (1)
##

## Store the previous exit status to propagate to the compiler
## export pash_previous_exit_status=$?
## The assignment now happens outside
export pash_previous_exit_status

## Store the current `set` status to pash to the inside script 
export pash_previous_set_status=$-

pash_redir_output echo "$$: (1) Previous exit status: $pash_previous_exit_status"
pash_redir_output echo "$$: (1) Previous set state: $pash_previous_set_status"

## Prepare a file with all shell variables
##
## This is only needed by PaSh to expand.
##
## TODO: Maybe we can get rid of it since PaSh has access to the environment anyway?
pash_runtime_shell_variables_file="$($RUNTIME_DIR/pash_ptempfile_name.sh $distro)"
source "$RUNTIME_DIR/pash_declare_vars.sh" "$pash_runtime_shell_variables_file"
pash_redir_output echo "$$: (1) Bash variables saved in: $pash_runtime_shell_variables_file"

## Abort script if variable is unset
pash_default_set_state="huB"

## Revert the `set` state to not have spurious failures 
pash_redir_output echo "$$: (1) Bash set state at start of execution: $pash_previous_set_status"
source "$RUNTIME_DIR/pash_set_from_to.sh" "$pash_previous_set_status" "$pash_default_set_state"
pash_redir_output echo "$$: (1) Set state reverted to PaSh-internal set state: $-"

##
## (2)
##

## The first argument contains the sequential script. Just running it should work for all tests.
pash_sequential_script_file=$1

## The second argument SHOULD be the file that contains the IR to be compiled 
pash_input_ir_file=$2

## The parallel script will be saved in the following file if compilation is successful.
pash_compiled_script_file="$($RUNTIME_DIR/pash_ptempfile_name.sh $distro)"


if [ "$pash_speculation_flag" -eq 1 ]; then
    ## Count the execution time
    pash_exec_time_start=$(date +"%s%N")
    source "$RUNTIME_DIR/pash_runtime_quick_abort.sh"
    pash_runtime_final_status=$?
    ## For now this will fail!!!
    exit 1
else
    ## TODO: Have a more proper communication protocol
    ## TODO: Make a proper client for the daemon
    echo "Compile:${pash_compiled_script_file}| Variable File:${pash_runtime_shell_variables_file}| Input IR File:${pash_input_ir_file}" > "$RUNTIME_IN_FIFO"
    daemon_response="$(cat $RUNTIME_OUT_FIFO)"
    pash_redir_output echo "$$: (2) Daemon responds: $daemon_response"
    if [[ "$daemon_response" == *"OK:"* ]]; then
        pash_runtime_return_code=0
    else
        pash_runtime_return_code=1
    fi

    pash_redir_output echo "$$: Compiler exited with code: $pash_runtime_return_code"
    if [ "$pash_runtime_return_code" -ne 0 ] && [ "$pash_assert_compiler_success_flag" -eq 1 ]; then
        pash_redir_output echo "$$: ERROR: Compiler failed with error code: $pash_runtime_return_code"
        exit 1
    fi

    ##
    ## (3)
    ##

    ## Count the execution time
    pash_exec_time_start=$(date +"%s%N")

    ## If the compiler failed or if we dry_run the compiler, we have to run the sequential
    if [ "$pash_runtime_return_code" -ne 0 ] || [ "$pash_dry_run_compiler_flag" -eq 1 ]; then
        pash_script_to_execute="${pash_sequential_script_file}"
    else
        pash_script_to_execute="${pash_compiled_script_file}"
    fi

    ##
    ## (4)
    ##
    source "$RUNTIME_DIR/pash_wrap_vars.sh" ${pash_script_to_execute}
    pash_runtime_final_status=$?

    ## We only want to execute (5) and (6) if we are in debug mode and it is not explicitly avoided
    if [ "$PASH_DEBUG_LEVEL" -ne 0 ] && [ "$pash_avoid_pash_runtime_completion_flag" -ne 1 ]; then
        ##
        ## (5)
        ##

        ## Prepare a file for the output shell variables to be saved in
        pash_output_variables_file="$($RUNTIME_DIR/pash_ptempfile_name.sh $distro)"
        # pash_redir_output echo "$$: Output vars: $pash_output_variables_file"

        ## Prepare a file for the `set` state of the inner shell to be output
        pash_output_set_file="$($RUNTIME_DIR/pash_ptempfile_name.sh $distro)"

        source "$RUNTIME_DIR/pash_runtime_shell_to_pash.sh" ${pash_output_variables_file} ${pash_output_set_file}

        ##
        ## (6)
        ##
        source "$RUNTIME_DIR/pash_runtime_complete_execution.sh"
    fi
fi

