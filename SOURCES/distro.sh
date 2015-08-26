#!/bin/bash -e

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
