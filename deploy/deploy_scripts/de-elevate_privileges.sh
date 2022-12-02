#!/usr/bin/env bash

# Script to lower privileges from sudo to the given user
# REF: https://stegard.net/2018/03/run-shell-script-as-different-user-with-proper-argument-handling/
# sudo ORIGINAL_USER=${ORIGINAL_USER} ./de-elevate_privileges.sh <command to run>

# This script must run as
RUN_AS=${ORIGINAL_USER}

if [[ `id -nu` != $RUN_AS ]]; then
    if [ `id -u` -ne 0 ]; then
        echo >&2 "Sorry, you must be either root or $RUN_AS to run me."
        exit 1
    fi

    # This environment variable is just a safe guard for endless re-exec loop
    # and something the script can use to test up to this point if it has
    # dropped privileges by re-executing itself
    if [[ "$EXEC_SU" ]]; then
        echo >&2 "Re-exec loop circuit breaker engaged, something is wrong"
        exit 1
    fi

    exec su $RUN_AS -s /bin/sh -c "EXEC_SU=1 \"$0\" \"\$@\"" -- "$0" "$@"
fi

# At this point, we can be sure we are running as the desired user.
# echo Running as `id -nu`
bash -c "$@"
