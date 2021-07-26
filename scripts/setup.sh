#!/bin/bash -e

# Copyright © 2015 Jason Stafford
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from /usr/include/sysexits.h
#	EX_CONFIG -- Something was found in an unconfigured
#		or miscon­figured state.
EX_CONFIG=78

# the following join function comes from
# http://stackoverflow.com/questions/1527049/bash-join-elements-of-an-array
function join { local IFS="$1"; shift; echo "$*"; }

if [ -f "/proc/version" ]; then
  proc_version=`cat /proc/version`
else
  proc_version=`uname -a`
fi

if [[ $proc_version != *"Red Hat"* ]]; then
  echo -e "\nERROR: Your OS is not yet supported by this script!\nYou'll need to setup the rpm build environment manually.\n" 1>&2
  exit $EX_CONFIG
fi

if [ "$EUID" -gt 0 ]; then
  echo "Please run this script as root as we *may* need to install packages."
  exit $EX_CONFIG
fi

PACKAGES_NEEDED=('wget' 'openssl' 'coreutils')
PACKAGES_TO_INSTALL=()

for pkg in ${PACKAGES_NEEDED[@]}; do
  echo -n "Checking '${pkg}'..."
  yum list installed | grep -o ${pkg} &>/dev/null
  if [ "$?" -ne "0" ]; then
    PACKAGES_TO_INSTALL+=($pkg)
    echo ' To be installed'
  else
    echo ' Installed'
  fi
done

if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then 
  # Make sure we have the repos enabled, other wise the install step will fail.
  repos=('epel' 'extras')
  repo_string=$(join "|" "${repos[@]}")
  needed_repo_count="${#repos[*]}"
  system_repo_count=$(yum repolist | grep -oE "${repo_string}" | sort -u | wc -l)

  if [ "$system_repo_count" -ne "$needed_repo_count" ]; then
    echo "Please make sure following repos are enabled as they are needed to install some packages: ${repo_string}"
    echo "Reference: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Deployment_Guide/sec-Managing_Yum_Repositories.html"
    exit $EX_CONFIG
  fi

  PACKAGES_STRING=$(join " " "${PACKAGES_TO_INSTALL[@]}")
  yum install -y "$PACKAGES_STRING"
fi

echo "Setup completed. Please run build.sh."
