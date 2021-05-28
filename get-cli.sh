#!/bin/sh

set -o errexit
set -o nounset

# BrainFrame CLI Installation Script
#
# Welcome in! This script is meant to make installation of the BrainFrame CLI
# easier for developers and manually deployed machines.
#
# WARNING: Please verify that the contents of this script match the version
#          found on the latest tagged release before running.
#          https://github.com/aotuai/brainframe-cli
#
# Thank you for trying BrainFrame!
#
#   ____                               ____
# /\  _`\                  __        /\  _`\
# \ \ \L\ \  _ __    __   /\_\    ___\ \ \L\_\_ __    __      ___ ___      __
#  \ \  _ <'/\`'__\/'__`\ \/\ \ /' _ `\ \  _\/\`'__\/'__`\  /' __` __`\  /'__`\
#   \ \ \L\ \ \ \//\ \L\.\_\ \ \/\ \/\ \ \ \/\ \ \//\ \L\.\_/\ \/\ \/\ \/\  __/
#    \ \____/\ \_\\ \__/.\_\\ \_\ \_\ \_\ \_\ \ \_\\ \__/.\_\ \_\ \_\ \_\ \____\
#     \/___/  \/_/ \/__/\/_/ \/_/\/_/\/_/\/_/  \/_/ \/__/\/_/\/_/\/_/\/_/\/____/

binary_url="https://aotu.ai/releases/brainframe-cli/brainframe"

with_root=""

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

download_file() {
  curl \
    --fail \
    --silent \
    --show-error \
    --location \
    "$1" \
    --output "$2"
}

get_distro_name() {
  # /etc/os-release should be present on all systemd Linux distros, which is
  # all of them we intend to support for now
  if [ -r /etc/os-release ]; then
    distro_name_output="$(. /etc/os-release && echo "$ID")"
  else
    >&2 echo "Missing /etc/os-release file. Unable to determine the current Linux"
    >&2 echo "distribution."
    exit 1
  fi
  echo "$distro_name_output"
}

get_distro_version() {
  case "$1" in
    ubuntu)
      distro_version_output="$(. /etc/lsb-release && echo "$DISTRIB_CODENAME")"
    ;;
    *)
      distro_version_output="unknown"
    ;;
  esac

  echo "$distro_version_output"
}

find_root_command() {
  if [ "$USER" = "root" ]; then
    with_root=""
  else
    if command_exists sudo; then
      # --reset-timestamp ensures that the user is always prompted for their
      # password
      with_root="sudo --reset-timestamp --preserve-env"
    elif command_exists su; then
      with_root="su -c"
    else
      >&2 echo "This script must run some commands with root permissions, but neither sudo nor"
      >&2 echo "su are available to accomplish that."
    fi
  fi
}

group_exists() {
  getent group "$1"
}

install_on_ubuntu() {
  echo ""

  if ! command_exists docker; then
    echo "Docker is not installed. The latest stable version will be installed now using"
    echo "the official get-docker.sh script."
    echo ""
    echo "    Alternatively, you may press Ctrl-C to stop this script and install Docker"
    echo "    manually."
    echo ""
    ( set -x; sleep 10 )

    echo ""
    echo "Downloading the get-docker.sh script..."
    download_file https://raw.githubusercontent.com/docker/docker-install/master/install.sh /tmp/get-docker.sh

    echo ""
    echo "[!] Running the get-docker.sh script. This requires root permissions."
    $with_root sh /tmp/get-docker.sh
  fi

  >&2 echo "Unimplemented"
  exit 1
}

install_on_unsupported() {
  >&2 echo ""
  >&2 echo "WARNING: Unsupported OS detected, falling back to binary installation."
  >&2 echo "         BrainFrame may still work, but full functionality is not guaranteed."
  >&2 echo ""

  if ! command_exists docker; then
    >&2 echo "Docker is not installed! Please install Docker and run this script again."
  fi

  if ! command_exists docker-compose; then
    >&2 echo "Docker Compose is not installed! Please install Docker Compose and run this script again."
  fi

  if ! group_exists brainframe; then
    echo ""
    echo "[!] Creating the 'brainframe' group. This requires root permissions."
    $with_root groupadd brainframe --gid 1337
  fi

  echo "Downloading the BrainFrame CLI binary..."
  download_file "$binary_url" /tmp/brainframe

  echo ""
  echo "[!] The BrainFrame CLI will now be installed. This requires root permissions."
  $with_root cp /tmp/brainframe /usr/local/bin/brainframe && chmod +x /usr/local/bin/brainframe
}

install_cli() {
  echo "BrainFrame CLI installation script"
  echo "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
  echo ""

  if command_exists brainframe; then
    >&2 echo "It looks like the BrainFrame CLI is already installed! Please"
    >&2 echo "uninstall the existing version first."
    exit 1
  fi

  find_root_command

  distro_name=$( get_distro_name )
  distro_version=$( get_distro_version "$distro_name" )

  case "$distro_name" in
    ubuntu)
      case "$distro_version" in
        bionic|focal)
          install_on_ubuntu
        ;;
        *)
          install_on_unsupported
        ;;
      esac
    ;;
    *)
      install_on_unsupported
    ;;
  esac

  echo ""
  echo "The BrainFrame CLI is now installed! You can now run 'brainframe install' to get"
  echo "the latest version of the BrainFrame server."
}

# Ensure that installation only runs if the entire file has been downloaded
install_cli
