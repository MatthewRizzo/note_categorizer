#!/usr/bin/env bash

function usage {
    cat << EOF
$(basename "${0}"): Loads the service files
General: ./$(basename "${0}") --user <ORIGINAL_USER>

The service files are placed in a user systemd context
Hence they must be loaded WITHOUT sudo privileges.
By putting the commands in this script, the main script (with sudo) can
use the de-elevate script to run it back as user

Required Args:
    -s | --service: The name of the service to load
Optional Args:
    -h | --help: Print this message
EOF
}

# $1 = service name
function load_service() {
    local -r service_name="$1"
    systemctl --user daemon-reload

    # Reference on user systemd files
    # https://wiki.archlinux.org/title/systemd/User#How_it_works
    systemctl --user stop ${service_name}
    # refresh service daemons
    systemctl --user daemon-reload
    systemctl --user start ${service_name}
}

function main() {
    local ORIGINAL_USER=""
    local service_name=""

    if [ "$EUID" -eq 0 ]; then
        echo "This scirpt MUST be run without sudo privileges"
        usage
        exit 1
    fi

    while [[ $# -gt 0 ]]; do
        arg="$1";
        shift;
        case ${arg} in
            "-h" | "--help")
                usage
                exit
                ;;
            "-s" | "--service")
                service_name="$1"
                shift
                ;;
        esac
    done

    if [[ "${service_name}" == "" ]]; then
        echo "Please add --service <service_file_name> "
        usage
        exit 1
    fi

    load_service ${service_name}
}

main $@
