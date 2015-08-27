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
#	EX_UNAVAILABLE -- A service is unavailable.  This can occur
#		if a support program or file does not exist.  This
#		can also be used as a catchall message when something
#		you wanted to do doesn't work, but you don't know
#		why.
EX_UNAVAILABLE=69

if [ -f "/proc/version" ]; then
  proc_version=`cat /proc/version`
else
  proc_version=`uname -a`
fi

if [[ $proc_version == *"Debian"* ]]; then
  distro=Debian
elif [[ $proc_version == *"Red Hat"* ]]; then
  distro=RedHat
elif [[ $proc_version == *"Ubuntu"* ]]; then
  distro=Ubuntu
elif [[ $proc_version == *"SUSE"* ]]; then
  distro=SUSE
else
  echo -e "\nERROR: Your Linux distribution ($proc_version) not supported!" 1>&2
  exit $EX_UNAVAILABLE
fi
