#!/bin/bash -e

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
#elif [[ $proc_version == *"Red Hat"* ]]; then
#  distro=RedHat
#elif [[ $proc_version == *"Ubuntu"* ]]; then
#  distro=Ubuntu
#elif [[ $proc_version == *"SUSE"* ]]; then
#  distro=SUSE
else
  echo -e "\nERROR: Your OS ($proc_version) is not yet supported by this script!\nYou'll need to setup the rpm build environment manually.\n" 1>&2
  exit EX_CONFIG
fi
