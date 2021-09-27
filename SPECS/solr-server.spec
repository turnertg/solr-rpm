# Copyright (c) 2015 Jason Stafford
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

# It's dangerous to go alone, take this: https://rpm-packaging-guide.github.io

# Disable repacking of jars, since it takes forever
# and it is not needed since there are no platform dependent jars in the archive
%define __jar_repack %{nil}

# path where solr will be installed
%define solr_install_dir /usr/share/solr-%{solr_version}
# path where solr will log
%define solr_log_dir /var/log/solr
# path where solr stores its data
%define solr_data_dir /var/lib/solr
# path where solr configurations will be stored
%define solr_config_dir /etc/solr
# binary files that allow us to control solr
%define solr_bin_dir /usr/bin
# path where runtime files (like PID file) will be located
%define solr_run_dir /run/solr
# directory for holding file that contains environment variables
%define solr_env_dir /etc/default
# matches SOLR_USER in the install_solr_service.sh file
%define solr_user solr
# matches SOLR_PORT in the install_solr_service.sh file
%define solr_port 8983

Name:           solr-server
Version:        %{solr_version}
Release:        %{rpm_release}
Summary:        Solr is the popular, blazing-fast, open source enterprise search platform built on Apache Lucene™
# We download and verify the binary archive in build.sh
Source0:        solr-%{solr_version}.tgz
URL:            http://lucene.apache.org/solr/
Group:          System Environment/Daemons
License:        Apache License, Version 2.0
Requires:       java-11-openjdk-headless, systemd, lsof, gawk, coreutils, shadow-utils
BuildArch:      noarch
BuildRequires:  tar, sed, coreutils
Vendor:         Apache Software Foundation
Obsoletes:      %{name} < %{version}

%description
Solr is an open source enterprise search server based on the Lucene Java search
library, with XML/HTTP and JSON APIs, hit highlighting, faceted search,
caching, replication, and a web administration interface. It runs in a Java 
servlet container such as Jetty.

This package provides binaries for running the server distribution
from the official website in RPM form. It includes embedded Jetty.

%prep
%setup -q -b 0 -n solr-%{solr_version}
# Copy SystemD service / tmpfile config to build dir because rpm-build is too stupid to handle flat files
cp -r %{_topdir}/../solr-rpm/systemd/* %{_builddir}

# Do some substitutions in scripts and configs to reflect constants defined in this spec file.
# Substitutions in place of patches will make maintenance easier.
solr_env_file='%{_builddir}/solr-%{solr_version}/bin/solr.in.sh'
sed -i'' 's|^#SOLR_PID_DIR.*$|SOLR_PID_DIR="%{solr_run_dir}"|g' $solr_env_file
sed -i'' 's|^#SOLR_HOME.*$|SOLR_HOME="%{solr_config_dir}"|g' $solr_env_file
sed -i'' 's|^#SOLR_LOGS_DIR.*$|SOLR_LOGS_DIR="%{solr_log_dir}"|g' $solr_env_file
sed -i'' 's|^#SOLR_PORT.*$|SOLR_PORT="%{solr_port}"|g' $solr_env_file
sed -i'' 's|^#SOLR_DATA_HOME.*$|SOLR_DATA_HOME="%{solr_data_dir}"|g' $solr_env_file

# Append DEFAULT_SERVER_DIR to solr_env_file so that embedded tools can work.
# It is not there in env file supplied by the package and is hard coded to be
# used in function run_tool(). 
echo -e '\n# Directory where the server code resides.' | tee -a $solr_env_file
echo -e 'DEFAULT_SERVER_DIR="%{solr_install_dir}/server"\n' | tee -a $solr_env_file

# Similar to DEFAULT_SERVER_DIR, set SOLR_TIP because SOLR_HOME is ignored
# and value of SOLR_TIP is supplied to -Dsolr.install.dir during startup.
echo -e '\n# Directory where solr is installed.' | tee -a $solr_env_file
echo -e 'SOLR_TIP="%{solr_install_dir}"\n' | tee -a $solr_env_file

# Change the location of oom_solr.sh when starting up solr in 'solr' script.
sed -i 's|$SOLR_TIP/bin/oom_solr.sh|%{solr_bin_dir}/oom_solr.sh|g' bin/solr

# Update paths in service definition
systemd_unit_file="%{_builddir}/solr-server.service"
sed -i'' 's|RPM_PORT|%{solr_port}|g' $systemd_unit_file
sed -i'' 's|RPM_ENV_DIR|%{solr_env_dir}|g' $systemd_unit_file
sed -i'' 's|RPM_RUN_DIR|%{solr_run_dir}|g' $systemd_unit_file
sed -i'' 's|RPM_BIN_DIR|%{solr_bin_dir}|g' $systemd_unit_file
sed -i'' 's|RPM_INSTALL_DIR|%{solr_install_dir}|g' $systemd_unit_file

# Update path in tmp file definition
tmpdir_definition="%{_builddir}/solr.conf"
sed -i'' 's|RPM_RUN_DIR|%{solr_run_dir}|g' $tmpdir_definition

# Because we are not packaging dist and 'post' script depends on it,
# change the path of solr-core.*.jar to the one that is packaged here.
# Source code analysis shows the util class used by 'post' script is
# there in solr-core in server too.
sed -i 's|"$SOLR_TIP/dist"|%{solr_install_dir}/server/solr-webapp/webapp/WEB-INF/lib|g' bin/post
 
%build

%install
rm -rf "%{buildroot}"

# make all directories.
for dir in \
  %{solr_install_dir} \
  %{solr_log_dir} \
  %{solr_run_dir} \
  %{solr_data_dir} \
  %{solr_config_dir} \
  %{solr_bin_dir} \
  %{solr_env_dir} \
  /usr/lib/systemd/system \
  /usr/lib/tmpfiles.d
do
  %__install -d "%{buildroot}$dir"
done

# install the main solr package in solr_install_dir
solr_root="%{_builddir}/solr-%{solr_version}"
cp -Rp "$solr_root/server" "%{buildroot}%{solr_install_dir}/"

# Do not copy Windows specific things and files that will not be living in bin folder
for file in oom_solr.sh post postlogs solr; do
  cp -Rp "$solr_root/bin/$file" "%{buildroot}%{solr_bin_dir}/$file"
done

# Consolidate Solr config. (this does not handle jetty config)
rpmtree_solr_dir="%{buildroot}%{solr_install_dir}/server"
cp -p $solr_root/bin/solr.in.sh "%{buildroot}%{solr_env_dir}/"

# Move the configs from server/solr to solr_config_dir
mv "$rpmtree_solr_dir/solr/zoo.cfg" "%{buildroot}%{solr_config_dir}/"
mv "$rpmtree_solr_dir/solr/solr.xml" "%{buildroot}%{solr_config_dir}/"

# Remove the solr folder from $solr_root/server because it is empty at this 
# point and will not be used.
rm -rf $rpmtree_solr_dir/solr

# install the systemd unit definition
%__install -m0744 %{_builddir}/solr-server.service "%{buildroot}/usr/lib/systemd/system/"

# install the systemd tmpfile definition to create /run/solr on system start.
%__install -m0744 %{_builddir}/solr.conf "%{buildroot}/usr/lib/tmpfiles.d/"

# copy licenses and other text files.
cp -Rp $solr_root/licenses %{buildroot}%{solr_install_dir}/
cp -p  $solr_root/*.txt %{buildroot}%{solr_install_dir}/

%pre
# add the user if it doesn't exist
id -u %{solr_user} &> /dev/null
if [ "$?" -ne "0" ]; then
  useradd --comment "System user to run solr daemon." --home-dir %{solr_data_dir} --system -M --shell /usr/sbin/nologin --user-group %{solr_user}
fi

%post
# reload systemctl daemon definitions
systemctl daemon-reload

%preun
# unmask and disable if uninstalling to clean up /etc/systemd symlinks
if [ "$1" == 0 ]; then
    systemctl unmask %{solr_service}
    systemctl disable %{solr_service}
fi
# stop the service regardless for data integrity's sake
echo "Stopping solr-server..."
systemctl stop solr-server

%postun
# delete the user and reload daemons if this is uninstallation as opposed to upgrade
if [ "$1" == 0 ]; then
    userdel %{solr_user}
    systemctl daemon-reload
fi

%clean
%__rm -rf "%{buildroot}"

%files
%defattr(0644,%{solr_user},%{solr_user},0755)
%dir %{solr_run_dir}
%dir %{solr_install_dir}
%{solr_log_dir}
%{solr_install_dir}
%{solr_data_dir}
%{solr_config_dir}
%attr(0644,root,root) /usr/lib/tmpfiles.d/solr.conf
%attr(0644,%{solr_user},%{solr_user}) /usr/lib/systemd/system/solr-server.service
%attr(0644,%{solr_user},%{solr_user}) %{solr_env_dir}/solr.in.sh
%attr(0755,%{solr_user},%{solr_user}) %{solr_bin_dir}/solr
%attr(0755,%{solr_user},%{solr_user}) %{solr_bin_dir}/post
%attr(0755,%{solr_user},%{solr_user}) %{solr_bin_dir}/postlogs
%attr(0755,%{solr_user},%{solr_user}) %{solr_bin_dir}/oom_solr.sh
%config(noreplace) %{solr_config_dir}/solr.xml
%config(noreplace) %{solr_config_dir}/zoo.cfg

%changelog
* Mon Sep 13 2021 turnertg@uw.edu
- It's more sensible to require OpenJDK 11 instead of 8, solr doesn't extensively test against 8 anymore

* Fri Jul 30 2021 turnertg@uw.edu
- Removed some customization for some standard and well-known systemd paths
- Removed ability to concurrently install several versions of solr - now obsoletes and upgrades
- Allow rpm to do handle config files and cut down on upgrade shell logic
- Changed upgrade logic to be less invasive, only stops the service on upgrade for safety reasons
- Log shouldn't be owned by the package for forensics and admin purposes

* Mon Jul 26 2021 turnertg@uw.edu
- Updated to support latest solr (8.9.0)
- Misc cleanup to better integrate with docker build process

* Wed Nov 15 2017 talk@devghai.com
- Added config to /usr/lib/tmpfiles.d to create /run/solr on startup

* Wed Feb 22 2017 talk@devghai.com
- Splitting data and core config directories
- Solr changes (v4.0.0 & above): http://archive.apache.org/dist/lucene/solr/%{solr_version}/changes/Changes.html

* Wed Feb 15 2017 talk@devghai.com
- Packaging for CentOS
- Solr changes (v4.0.0 & above): http://archive.apache.org/dist/lucene/solr/%{solr_version}/changes/Changes.html

* Wed Aug 26 2015 jks@sagevoice.com
- Inital version
