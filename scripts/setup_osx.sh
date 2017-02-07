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

# Check if Ruby is installed.
if ! hash ruby 2>/dev/null; then
  echo "\nERROR: Ruby needs to be installed. It is needed to install brew, if not there on your system." 1>&2
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

# check for openssl
if ! hash openssl 2>/dev/null; then
  brew install openssl
fi
