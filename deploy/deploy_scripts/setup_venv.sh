#!/usr/bin/env bash
# Script responsible for installing poetry (if needed) and creating the virtual
# environment.
# NOTE: This script MUST be run WITHOUT sudo

readonly PYTHON_VERSION="3.10"
readonly PYTHON="python${PYTHON_VERSION}"

readonly PROJECT_DEPLOY_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
readonly PROJECT_ROOT_DIR=$(realpath ${PROJECT_DEPLOY_DIR}/../)
readonly POETRY_LOCK_FILE=${PROJECT_ROOT_DIR}/poetry.lock
readonly SOURCE_CWD=${PWD}

# Location of the created venv. Set once it is created
venv_location=""

function usage {
    cat << EOF
$(basename "${0}"): Sets up the virtual environment
General: ./$(basename "${0}") --user <ORIGINAL_USER>

The virtual environment used by the project is done with Poetry.
The script attempts to install Poetry and then uses it to create the virtual
environment within the project.

Note: poetry MUST be installed at the user level. Hence this script CANNOT get
run with sudo permissions.

Required Args:
    -u | --user: The actual user calling the script (not sudo)
Optional Args:
    -h | --help: Print this message
EOF
}

# Adding poetry to path is necessary for it to work
# Check if the path is already added, if not, add an source for it in
# ~/.bashrc
# $1 = user
function add_local_to_path() {
    local -r user=$1
    local -r path_to_add="/home/${user}/.local/bin/"
local -r cmd_to_print=$(cat <<END_HEREDOC

PATH="\$PATH:$path_to_add"
END_HEREDOC
)
    if ! echo "$PATH" | /bin/grep -Eq "(^|:)${path_to_add}($|:)" ; then
        echo "Adding ${path_to_add} to path"
        echo "$cmd_to_print" >> /home/${user}/.bashrc
        source /home/${user}/.bashrc
    fi
}

# $1 = user
function install_poetry() {
    local -r user="$1"
    curl_cmd="curl -sSL https://install.python-poetry.org"
    install_script_cmd="${PYTHON} - --version 1.2.2"
    local -r install_cmd="${curl_cmd} | ${install_script_cmd}"
    echo "${curl_cmd} | bash -c \"${install_script_cmd}\""
    ${curl_cmd} | bash -c "${install_script_cmd}"

    if ! command poetry &> /dev/null; then
        add_local_to_path ${user}
    fi
}

# Installs the virtual environment defined by poetry, using poetry
function setup_poetry_venv() {
    cd ${PROJECT_ROOT_DIR}

    local -r get_venv_path_cmd="poetry env info --path"

    #  Makes sure to install venv in local dir
    poetry config --local virtualenvs.in-project true

    poetry install
    # Poetry defaults to creating the venv in the local project
    venv_location="${PROJECT_ROOT_DIR}/.venv"
    cd ${SOURCE_CWD}
}


# $1 = user
function main() {
    local ORIGINAL_USER=""

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
            "-u" | "--user")
                ORIGINAL_USER="$1"
                shift
                ;;
        esac
    done

    if [[ "$ORIGINAL_USER" == "" ]]; then
        echo "Please add --user <non_sudo_user> "
        usage
        exit 1
    fi

    install_poetry ${ORIGINAL_USER}
    setup_poetry_venv

    #  Echo out the venv location so scripts calling it can capture the output
    VENV_LOCATION=${venv_location}
}

main $@
