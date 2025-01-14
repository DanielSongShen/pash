#!/usr/bin/env bash

## TODO: Give it the output pid as an argument
## TODO pass the distro version via the python script
wait $@
if type lsb_release >/dev/null 2>&1 ; then
    distro=$(lsb_release -i -s)
elif [ -e /etc/os-release ] ; then
    distro=$(awk -F= '$1 == "ID" {print $2}' /etc/os-release)
fi

# convert to lowercase
distro=$(printf '%s\n' "$distro" | LC_ALL=C tr '[:upper:]' '[:lower:]')
# now do different things depending on distro
case "$distro" in
    freebsd*)  
        # not sure at all about this one
        pids_to_kill="$(ps -efl $$ |awk '{print $1}' | grep -E '[0-9]')"
        ;;
    *)
        pids_to_kill="$(ps --ppid $$ |awk '{print $1}' | grep -E '[0-9]')"
        ;;
esac
for pid in $pids_to_kill
do
    (> /dev/null 2>&1 kill -SIGPIPE $pid || true)
done
