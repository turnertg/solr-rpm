#!/bin/bash -e

# from /usr/include/sysexits.h
#	EX_USAGE -- The command was used incorrectly, e.g., with
#		the wrong number of arguments, a bad flag, a bad
#		syntax in a parameter, or whatever.
EX_USAGE=64
#	EX_DATAERR -- The input data was incorrect in some way.
#		This should only be used for user's data & not
#		system files.
EX_DATAERR=65

if [ $# -ne 2 ]
then
  echo "Exactly two arguments are required. For example './build.sh 5.3.0 1' where '5.3.0' can be replaced by any released version of Solr and the second parameter is the version of the rpm itself"
  exit $EX_USAGE
fi

SOLR_VERSION="$1"
RPM_RELEASE="$2"

# clean the working directories
rm -rf BUILD RPMS SRPMS tmp || true
mkdir -p BUILD RPMS SRPMS tmp

# download the sources
if [ ! -d SOURCES ]
then
  mkdir SOURCES
fi

if [ ! -f SOURCES/solr-$SOLR_VERSION.tgz ]
then
  # download the list of mirror sites
  wget -O tmp/mirrors.html http://www.apache.org/dyn/closer.cgi/lucene/solr/$SOLR_VERSION
  # use hxwls from the w3.org html-xml-utils package to get the links out of the html file
  ALL_LINKS=$(hxwls tmp/mirrors.html)
  # grab the fist link that contains the version we are looking for
  DOWNLOAD_LINK=$(grep -m 1 "$SOLR_VERSION" <<< "$ALL_LINKS")
  # actually download the archive from the mirror	
  wget -O SOURCES/solr-$SOLR_VERSION.tgz $DOWNLOAD_LINK/solr-$SOLR_VERSION.tgz
fi

# get the SHA1 from Apache directly
if [ ! -f SOURCES/solr-$SOLR_VERSION.tgz.sha1 ]
then
  wget -O SOURCES/solr-$SOLR_VERSION.tgz.sha1 http://archive.apache.org/dist/lucene/solr/$SOLR_VERSION/solr-$SOLR_VERSION.tgz.sha1
fi 

# verify the integrity of the archive
# the sha1 file has the file name at the end, so use a regex to just pull the sha1 part out of the file
SHA1=$(<SOURCES/solr-$SOLR_VERSION.tgz.sha1)
SHA1_REGEX="^([0-9a-f]+)"
[[ $SHA1 =~ $SHA1_REGEX ]]
SHA1="${BASH_REMATCH[1]}"

# use openssl to generate the sha1 for the local archive
LOCAL_SHA1=$(openssl sha1 SOURCES/solr-$SOLR_VERSION.tgz)
# openssl puts the file name at the beginning, so use another regex to pull just the sha1
SHA1_REGEX="([0-9a-f]+)$"
[[ $LOCAL_SHA1 =~ $SHA1_REGEX ]]
LOCAL_SHA1="${BASH_REMATCH[1]}"

if [ $LOCAL_SHA1 == $SHA1 ]
then
  echo "SHA1 for SOURCES/solr-$SOLR_VERSION.tgz checks out"
else
  echo "ERROR! SOURCES/solr-$SOLR_VERSION.tgz has become corrupted or been tampered with.  Delete it and re-run this script."
  exit $EX_DATAERR
fi



