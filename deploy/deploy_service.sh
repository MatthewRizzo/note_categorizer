#!/usr/bin/env bash
# Script to deploy the service to a device.
# Copies the service file & environment to the correct location.
# At deploy time, it determines  environs such as user and path to the project.
# It stores them within the environment file. This is used when the service
# starts up.

function usage {
    cat << EOF
$(basename "${0}"): Deploys the Service file and starts the service
General: sudo ./$(basename "${0}")

The service files are placed in a user systemd context,
The virtual environment for the project is created,
and the service is started.

Note: this script MUST be run as sudo (to put the service file in
/usr/lib/systemd/user).

Required Args:
    None
Optional Args:
    -h | --help: Print this message
EOF
}



# Sudo related constants
readonly ORIGINAL_USER=${SUDO_USER}

readonly SERVICE_DEPLOY_SUFFIX="/usr/lib/systemd/user"
readonly ENV_DEPLOY_SUFFIX="/usr/lib/systemd/sysconfig"

readonly ACTUAL_SERVICE_DEPLOY_LOCATION=${SERVICE_DEPLOY_SUFFIX}
readonly ACTUAL_ENV_DEPLOY_LOCATION=${ENV_DEPLOY_SUFFIX}

readonly PROJECT_DEPLOY_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
readonly PROJECT_SERVICE_DEPLOY_LOCATION=${PROJECT_DEPLOY_DIR}${SERVICE_DEPLOY_SUFFIX}
readonly PROJECT_ENV_DEPLOY_LOCATION=${PROJECT_DEPLOY_DIR}${ENV_DEPLOY_SUFFIX}

readonly SERVICE_NAME="note-categorizer-web-app"
readonly PROJECT_SERVICE_FILENAME="${SERVICE_NAME}.service"
readonly PROJECT_ENVIRONMENT_FILENAME="${SERVICE_NAME}-env"

readonly ACTUAL_SERVICE_LOCATION=${ACTUAL_SERVICE_DEPLOY_LOCATION}/${PROJECT_SERVICE_FILENAME}

readonly PROJECT_ROOT_DIR="$(realpath ${PROJECT_DEPLOY_DIR}/../)"
readonly DEPLOY_SCRIPTS=${PROJECT_DEPLOY_DIR}/deploy_scripts
readonly WEB_APP_MAIN_PATH=${PROJECT_ROOT_DIR}/note_categorizer/web_app/main.py

readonly LOWER_PRIV_SCRIPT_NAME="de-elevate_privileges.sh"
readonly SETUP_VENV_SCRIPT_NAME="setup_venv.sh"
readonly GET_ENV_PATH_SCRIPT_NAME="get_venv_path.sh"
readonly LOAD_SERVICE_FILE_SCRIPT="load_service_file.sh"

# Location of the created venv. Set once it is created
venv_location=""

# Function to make it easy to run a command as a user
# $1 = the command to run as a user (as a string)
function run_as_user() {
    local -r user_cmd="$1"
    sudo ORIGINAL_USER=${ORIGINAL_USER} ${DEPLOY_SCRIPTS}/${LOWER_PRIV_SCRIPT_NAME} "${user_cmd}"
}

# Copies the service file to the REAL service location
function deploy_service_file(){
    echo "mkdir -p ${ACTUAL_SERVICE_DEPLOY_LOCATION}"
    mkdir -p ${ACTUAL_SERVICE_DEPLOY_LOCATION}
    local -r project_service_location=${PROJECT_SERVICE_DEPLOY_LOCATION}/${PROJECT_SERVICE_FILENAME}
    echo "Deploying Service File to ${ACTUAL_SERVICE_LOCATION}"
    sudo cp ${project_service_location} ${ACTUAL_SERVICE_LOCATION}
}

function setup_virtual_environment() {
    # Create the venv and save its location to the global script variable
    echo "Setting up virtual environment"
    local -r user_cmd="bash ${DEPLOY_SCRIPTS}/${SETUP_VENV_SCRIPT_NAME} --user ${ORIGINAL_USER}"
    run_as_user "${user_cmd}"

    # Poetry defaults to creating the venv in the local project
    venv_location="${PROJECT_ROOT_DIR}/.venv"
}

# Uses knowledge at run time to modify the default environment file.
# Copies the environment file to the correct location used by service file
# $1 = venv_location
# $2 = note_categorizer_root_dir
# $3 = web_app_main_path
function setup_environment_file() {
    local -r venv_location="$1"
    local -r project_root_dir="$2"
    local -r web_app_main_path="$3"

    local -r env_file_src_loc=${PROJECT_ENV_DEPLOY_LOCATION}/${PROJECT_ENVIRONMENT_FILENAME}
    local -r final_copied_env_loc=${ACTUAL_ENV_DEPLOY_LOCATION}/${PROJECT_ENVIRONMENT_FILENAME}
    echo "Deploying Service Environment file to ${final_copied_env_loc}"
    sudo mkdir -p ${ACTUAL_ENV_DEPLOY_LOCATION}

    #  Save past env files
    sudo mv ${final_copied_env_loc} ${final_copied_env_loc}.bkp

    # Copy the new one
    sudo cp ${env_file_src_loc} ${final_copied_env_loc}

    # Add new variables to it
    echo "venv_path=\"${venv_location}\"" >> ${final_copied_env_loc}
    echo "note_categorizer_root_dir=\"${project_root_dir}\"" >> ${final_copied_env_loc}
    echo "WEB_APP_MAIN_PATH=\"${web_app_main_path}\"" >> ${final_copied_env_loc}
}

function reload_service_files() {

    echo "Reloading the service"
    sudo systemctl --machine=${ORIGINAL_USER}@.host --user daemon-reload

    sudo systemctl --machine=${ORIGINAL_USER}@.host --user enable ${SERVICE_NAME}

    # Reference on user systemd files
    # https://wiki.archlinux.org/title/systemd/User#How_it_works
    sudo systemctl --machine=${ORIGINAL_USER}@.host --user stop ${SERVICE_NAME}

    # refresh service daemons
    sudo systemctl --machine=${ORIGINAL_USER}@.host --user daemon-reload
    sudo systemctl --machine=${ORIGINAL_USER}@.host --user start ${SERVICE_NAME}

    echo "Done loading service files!"

}

function main() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script MUST be run as root!"
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
        esac
    done

    setup_virtual_environment
    deploy_service_file
    setup_environment_file ${venv_location} ${PROJECT_ROOT_DIR} ${WEB_APP_MAIN_PATH}
    reload_service_files
}


main $@
