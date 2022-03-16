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
#	EX_USAGE -- The command was used incorrectly, e.g., with
#		the wrong number of arguments, a bad flag, a bad
#		syntax in a parameter, or whatever.
EX_USAGE=64
#	EX_DATAERR -- The input data was incorrect in some way.
#		This should only be used for user's data & not
#		system files.
EX_DATAERR=65
# EX_OSERR -- An operating system error has been detected.
#		This is intended to be used for such things as "cannot
#		fork", "cannot create pipe", or the like.  It includes
#		things like getuid returning a user that does not
#		exist in the passwd file.
EX_OSERR=71

if [ $EUID -eq 0 ]; then
  echo 'Please do not run this script as root.'
  echo 'See https://fedoraproject.org/wiki/How_to_create_an_RPM_package#Preparing_your_system for details.'
  exit $EX_OSERR
fi

if [ $# -ne 2 ]; then
  echo "Exactly two arguments are required. For example './build.sh 5.3.0 1' where '5.3.0' can be replaced by any released version of Solr and the second parameter is the version of the rpm itself"
  exit $EX_USAGE
fi

SOLR_VERSION="$1"
RPM_RELEASE="$2"

# validate the inputs
if [[ "$SOLR_VERSION" =~ ^[5-9]\.[0-9]+\.[0-9]+$ ]]; then
  echo "Using Solr version: $SOLR_VERSION"
else
  echo "Invalid Solr version format. Must be of the form x.x.x"
  echo "Solr versions above 5.0.0 and less than 10 are supported."
  exit $EX_USAGE
fi

# Set some necessary variables for grabbing the source
rpmbuild_path="$HOME/rpmbuild"
sources_path="$rpmbuild_path/SOURCES"
apache_archives='https://archive.apache.org/dist/lucene/solr/'
mirrors='/tmp/solr_mirrors.html'
archive="solr-$SOLR_VERSION.tgz"

# Move spec dir to build dir
cp -R $HOME/solr-rpm/SPECS $rpmbuild_path/

# download the list of mirror sites
wget -O $mirrors https://www.apache.org/dyn/closer.lua/lucene/solr/$SOLR_VERSION
#&>/dev/null

# append the archive site to end of file so that it is tried last if all mirrors fail
echo "$apache_archives$SOLR_VERSION/" | tee -a $mirrors &>/dev/null
successfully_downloaded=1
echo "Trying to download from..."
for mirror in $(grep -oP "(https.+?$SOLR_VERSION)?" $mirrors | uniq) ; do
    echo "* $mirror"
    # wget fails when there is a 404 and the script ends, even in subshell ( using $() )
    # Using && and || to capture success and failure respectively.
    # some mirrors automatically redirect to latest version. using --max-redirect=0 to avoid that.
    wget --max-redirect=0 -O $sources_path/$archive $mirror/$archive &>/dev/null && successfully_downloaded=0 || successfully_downloaded="$?"
    [ "$successfully_downloaded" -eq 0 ] && break
done

# cleanup and check if download was successful
rm $mirrors
if [ "$successfully_downloaded" -gt 0 ]; then
  echo -e "\nCould not download solr from mirrors."
  echo "You can download the file to $sources_path/$archive and rerun this script."
  echo "Following versions are available for download and packaging:"
  curl $apache_archives 2>&1 | grep -oP '[5-9]\.\d\.\d?' | uniq
  rm -f $sources_path/$archive
  exit 1
fi

# get the SHA512 from Apache directly
echo "Checking SHA512 hash..."
if [ ! -f $sources_path/$archive.sha512 ]; then
  wget -O $sources_path/$archive.sha512 "$apache_archives$SOLR_VERSION/$archive.sha512"
fi

# verify the integrity of the archive
# the sha512 file has the file name at the end, so use a regex to just pull the sha512 part out of the file
SHA512=$(<$sources_path/$archive.sha512)
[[ $SHA512 =~ ^([0-9a-f]+) ]]
SHA512="${BASH_REMATCH[1]}"

# use openssl to generate the sha512 for the local archive
LOCAL_SHA512=$(openssl sha512 $sources_path/$archive)

# openssl puts the file name at the beginning, so use another regex to pull just the sha512
[[ $LOCAL_SHA512 =~ ([0-9a-f]+)$ ]]
LOCAL_SHA512="${BASH_REMATCH[1]}"

# compare with known-good hash and fail if it's incorrect
if [ $LOCAL_SHA512 == $SHA512 ]; then
  echo "SHA512 for $sources_path/$archive checks out: $SHA512"
else
  rm -f $sources_path/solr*
  echo "ERROR! $sources_path/$archive download was not successful (checksum did not match)."
  echo "       The file has been deleted. Please rerun the script."
  exit $EX_DATAERR
fi

# Now that the sources are downloaded and verified we can actually make the RPM.
# _topdir and _tmppath are magic rpm variables that can be defined in ~/.rpmmacros
# For ease of reliable builds they are defined here on the command line.
rpmbuild -ba --define="_topdir $rpmbuild_path" --define="buildroot $rpmbuild_path/BUILDROOT" --define="solr_version $SOLR_VERSION" --define="rpm_release $RPM_RELEASE" $rpmbuild_path/SPECS/solr-server.spec

# Copy built packages to an easy to get at location
DEST_DIR=/tmp/solr-${SOLR_X_Y_Z_VERSION}-rpm
mkdir -p ${DEST_DIR}
cp ~/rpmbuild/RPMS/noarch/* ${DEST_DIR}
cp ~/rpmbuild/SRPMS/* ${DEST_DIR}
