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

# Some documentation to help reduce time to search
# https://fedoraproject.org/wiki/How_to_create_an_RPM_package#SPEC_file_overview

# Disable repacking of jars, since it takes forever
# and it is not needed since there are no platform dependent jars in the archive
%define __jar_repack %{nil}

# Rationale: http://www.pathname.com/fhs/pub/fhs-2.3.html#THEUSRHIERARCHY
%define solr_install_dir /usr/local/solr
# path where solr will log.
%define solr_log_dir /var/log/solr
# Rationale: http://www.pathname.com/fhs/pub/fhs-2.3.html#SRVDATAFORSERVICESPROVIDEDBYSYSTEM
%define solr_data_dir /srv/solr
# path where solr configurations will be stored
%define solr_config_dir /etc/solr
# binary files that allow us to control solr
%define solr_bin_dir /usr/local/bin/solr
# path where runtime files (like PID file) will be located
%define solr_run_dir /run/solr
# directory for holding file that contains environment variables
%define solr_env_dir /etc/default
# directory that will hold SystemD service definition for solr
%define solr_service_dir /lib/systemd/system
# matches SOLR_USER in the install_solr_service.sh file
%define solr_user solr
# matches SOLR_PORT in the install_solr_service.sh file
%define solr_port 8983
# matches SOLR_SERVICE in the install_solr_service.sh file
%define solr_service solr


Name:           solr-server
Version:        %{solr_version}
Release:        %{rpm_release}
Summary:        Solr is the popular, blazing-fast, open source enterprise search platform built on Apache Lucene™
# We download and verify the binary archive in build.sh
Source0:        %{name}-%{solr_version}.tgz
URL:            http://lucene.apache.org/solr/
Group:          System Environment/Daemons
License:        Apache License, Version 2.0
Requires:       java-1.8.0-openjdk-headless >= 1.8.0, systemd, lsof, gawk, coreutils
BuildArch:      noarch
Vendor:         Apache Software Foundation

%description
Solr is an open source enterprise search server based on the Lucene Java search
library, with XML/HTTP and JSON APIs, hit highlighting, faceted search,
caching, replication, and a web administration interface. It runs in a Java 
servlet container such as Jetty.

This package provides binaries for running the server distribution
from the official website in RPM form. It includes embedded Jetty.

%prep
# Copy SystemD service definition to SOURCES
cp %{_topdir}/extra/solr.service %{_sourcedir}/

%setup -q

%build

%install
rm -rf "%{buildroot}"

# make all directories.
for dir in %{solr_install_dir} %{solr_log_dir} %{solr_run_dir} %{solr_data_dir} %{solr_config_dir} %{solr_bin_dir} %{solr_env_dir} %{solr_service_dir}
do
  %__install -d "%{buildroot}$dir
done

# install the main solr package in solr_install_dir
cp -Rp solr-%{solr_version}/server/* "%{buildroot}%{solr_install_dir}/server/"

# Bin files/scripts.
# Do not copy Windows specific things and files that will not be living in bin folder.
for file in oom_solr.sh post solr; do
  cp -Rp solr-%{solr_version}/bin/$file "%{buildroot}%{solr_bin_dir}/$file"
done

# copy config
cp solr-%{solr_version}/server/solr/solr.xml "%{buildroot}%{solr_config_dir}/"
cp solr-%{solr_version}/bin/solr.in.sh "%{buildroot}%{solr_env_dir}/"
cp solr-%{solr_version}/server/resources/log4j.properties "%{buildroot}%{solr_config_dir}/"
sed_expr="s#solr.log=.*#solr.log=\${solr.solr.home}/../logs#"
sed -i.tmp -e "$sed_expr" "%{buildroot}%{solr_var_dir}/log4j.properties"
rm -f "%{buildroot}%{solr_var_dir}/log4j.properties.tmp"
echo "SOLR_PID_DIR=%{solr_var_dir}
SOLR_HOME=%{solr_var_dir}/data
LOG4J_PROPS=%{solr_var_dir}/log4j.properties
SOLR_LOGS_DIR=%{solr_var_dir}/logs
SOLR_PORT=%{solr_port}
" >> %{buildroot}%{solr_var_dir}/solr.in.sh

# install the systemd unit definition to /lib/systemd/system (works both on Debian and CentOS)
%__install -m0744 solr.service "%{buildroot}%{solr_service_dir}/"

# do some basic variable substitution on the init.d script
sed -i.tmp -e "$sed_expr1" -e "$sed_expr2" -e "$sed_expr3" -e "$sed_expr4" %{buildroot}/etc/init.d/%{solr_service}
rm -f %{buildroot}/etc/init.d/%{solr_service}.tmp

%pre
id -u %{solr_user} &> /dev/null
if [ "$?" -ne "0" ]; then
  # useradd is low-level utility and works on most distros.
  # -M Do no create the user's home directory, even if the system wide setting from
  #    /etc/login.defs (CREATE_HOME) is set to yes.
  # /usr/sbin/nologin exists on RedHat and Debian.
  useradd --comment "System user to run solr daemon." --home-dir %{solr_install_dir} --system -M --shell /usr/sbin/nologin --user-group %{solr_user}
fi
# Ensure directories needed exist.
dirs=%{solr_dirs}
for dir in ${dirs[@]}; do
  echo "Creating ${dir}..."
  mkdir -p $dir
  chown %{solr_user}:%{solr_user} ${dir}
done

%post
source distro.sh
if [[ "$distro" == "RedHat" || "$distro" == "SUSE" ]]; then
  chkconfig %{solr_service} on
else
  update-rc.d %{solr_service} defaults
fi
service %{solr_service} start
sleep 5

%preun
if [ "$1" == 0 ]; then
    # if this is uninstallation as opposed to upgrade, delete the service
    service %{solr_service} stop > /dev/null 2>&1
fi
exit 0

%postun
source distro.sh
if [ "$1" -ge 1 ]; then
    service solr restart > /dev/null 2>&1
elif [ "$1" == 0 ]; then
    # if this is uninstallation as opposed to upgrade, delete the service
    if [[ "$distro" == "RedHat" || "$distro" == "SUSE" ]]; then
      chkconfig --del %{solr_service}
    else
      update-rc.d %{solr_service} remove
    fi
    dirs=%{solr_dirs}
    for dir in ${dirs[@]}; do
      echo "Deleting ${dir}..."
      rom -rf $dir
    done
fi

exit 0

%clean
%__rm -rf "%{buildroot}"

%files
%attr(-,%{solr_user},-) %{solr_install_dir}
%dir %attr(-,%{solr_user},-) %{solr_var_dir}
%dir %attr(-,%{solr_user},-) %{solr_var_dir}/data
%config %attr(-,%{solr_user},-) %{solr_var_dir}/data/solr.xml
%dir %attr(-,%{solr_user},-) %{solr_var_dir}/logs
%config %attr(-,%{solr_user},-) %{solr_var_dir}/log4j.properties
%config %attr(-,%{solr_user},-) %{solr_var_dir}/solr.in.sh
%config %attr(0744,root,root) /etc/init.d/%{solr_service}

%changelog
* Solr changes (v4.0.0 & above): http://archive.apache.org/dist/lucene/%{name}/%{solr_version}/changes/Changes.html

* Wed Aug 26 2015 jks@sagevoice.com
- Inital version
