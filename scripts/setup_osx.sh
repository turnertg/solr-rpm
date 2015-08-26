#!/bin/bash -e

# from /usr/include/sysexits.h
#	EX_CONFIG -- Something was found in an unconfigured
#		or miscon­figured state.
EX_CONFIG=78

# check for fink
if hash fink 2>/dev/null; then
  echo -e "\nERROR: You appear to have fink installed.  This setup script only works with brew." 1>&2
  exit $EX_CONFIG
fi

# check for macports
if hash port 2>/dev/null; then
  echo -e "\nERROR: You appear to have macports installed.  This setup script only works with brew." 1>&2
  exit $EX_CONFIG
fi

# check for brew
if ! hash brew 2>/dev/null; then
  #install brew
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

# check for wget
if ! hash wget 2>/dev/null; then
  brew install wget
fi

# check for hxwls
if ! hash hxwls 2>/dev/null; then
  brew install html-xml-utils
fi

# check for rpmbuild
if ! hash rpmbuild 2>/dev/null; then
  brew install rpm
fi
