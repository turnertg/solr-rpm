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

if [ -f "/proc/version" ]; then
  proc_version=`cat /proc/version`
else
  proc_version=`uname -a`
fi

if [[ $proc_version == *"Darwin"* ]]; then
  /bin/bash scripts/setup_osx.sh
  exit $?
#elif [[ $proc_version == *"Debian"* ]]; then
#  distro=Debian
elif [[ $proc_version == *"Red Hat"* ]]; then
  /bin/bash scripts/setup_redhat.sh
  exit $?
#elif [[ $proc_version == *"Ubuntu"* ]]; then
#  distro=Ubuntu
#elif [[ $proc_version == *"SUSE"* ]]; then
#  distro=SUSE
else
  echo -e "\nERROR: Your OS ($proc_version) is not yet supported by this script!\nYou'll need to setup the rpm build environment manually.\n" 1>&2
  exit $EX_CONFIG
fi
