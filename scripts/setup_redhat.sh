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

# the following join function comes from
# http://stackoverflow.com/questions/1527049/bash-join-elements-of-an-array
function join { local IFS="$1"; shift; echo "$*"; }

PACKAGES=()

# check for wget
if ! hash wget 2>/dev/null; then
  PACKAGES+=("wget")
fi

# check for hxwls
if ! hash hxwls 2>/dev/null; then
  PACKAGES+=("html-xml-utils")
fi

# check for rpmbuild
if ! hash rpmbuild 2>/dev/null; then
  PACKAGES+=("rpm-build")
fi

if [ ${#PACKAGES[@]} -gt 0 ]; then
  PACKAGES_STRING=$(join " " "${PACKAGES[@]}")
  yum install "$PACKAGES_STRING"
fi
