# Disable repacking of jars, since it takes forever
# and it is not needed since there are no platform dependent jars in the archive
%define __jar_repack %{nil}

# matches SOLR_VAR_DIR in the install_solr_service.sh file
%define solr_var_dir /var/solr
# matches SOLR_INSTALL_DIR in the solr file in /etc/init.d/
%define solr_install_dir /opt/solr
# matches SOLR_USER in the install_solr_service.sh file
%define solr_user solr
# matches SOLR_PORT in the install_solr_service.sh file
%define solr_port 8983
# matches SOLR_SERVICE in the install_solr_service.sh file
%define solr_service solr


Name:           solr
Version:        %{solr_version}
Release:        %{rpm_release}
Summary:        APACHE SOLR™ %{solr_version}
Source:         solr-%{solr_version}.tgz
Source1:        distro.sh
URL:            http://lucene.apache.org/solr/
Group:          System Environment/Daemons
License:        Apache License, Version 2.0
BuildRoot:      %{_tmppath}/build-%{name}-%{version}
Requires:       unzip, awk, lsof, java >= 1.7.0
BuildArch:      noarch
Vendor:         Apache Software Foundation

%description
Solr is the popular, blazing-fast, open source enterprise search platform built on Apache Lucene™.

%prep
%setup -q -c
cp %{SOURCE1} .

%build

%install
rm -rf "%{buildroot}"

# install the main solr package in solr_install_dir
%__install -d "%{buildroot}%{solr_install_dir}"
cp -Rp solr-%{solr_version}/* "%{buildroot}%{solr_install_dir}"

# install the var dir for solr
%__install -d "%{buildroot}%{solr_var_dir}/data"
%__install -d "%{buildroot}%{solr_var_dir}/logs"
cp solr-%{solr_version}/server/solr/solr.xml "%{buildroot}%{solr_var_dir}/data/"
cp solr-%{solr_version}/bin/solr.in.sh "%{buildroot}%{solr_var_dir}/"
cp solr-%{solr_version}/server/resources/log4j.properties "%{buildroot}%{solr_var_dir}/"
sed_expr="s#solr.log=.*#solr.log=\${solr.solr.home}/../logs#"
sed -i.tmp -e "$sed_expr" "%{buildroot}%{solr_var_dir}/log4j.properties"
rm -f "%{buildroot}%{solr_var_dir}/log4j.properties.tmp"
echo "SOLR_PID_DIR=%{solr_var_dir}
SOLR_HOME=%{solr_var_dir}/data
LOG4J_PROPS=%{solr_var_dir}/log4j.properties
SOLR_LOGS_DIR=%{solr_var_dir}/logs
SOLR_PORT=%{solr_port}
" >> %{buildroot}%{solr_var_dir}/solr.in.sh

# install the daemon
%__install -d "%{buildroot}/etc/init.d"
%__install -m0744 solr-%{solr_version}/bin/init.d/solr "%{buildroot}/etc/init.d/%{solr_service}"
# do some basic variable substitution on the init.d script
sed_expr1="s#SOLR_INSTALL_DIR=.*#SOLR_INSTALL_DIR=%{solr_install_dir}#"
sed_expr2="s#SOLR_ENV=.*#SOLR_ENV=%{solr_var_dir}/solr.in.sh#"
sed_expr3="s#RUNAS=.*#RUNAS=%{solr_user}#"
sed_expr4="s#Provides:.*#Provides: %{solr_service}#"
sed -i.tmp -e "$sed_expr1" -e "$sed_expr2" -e "$sed_expr3" -e "$sed_expr4" %{buildroot}/etc/init.d/%{solr_service}
rm -f %{buildroot}/etc/init.d/%{solr_service}.tmp

%pre
source distro.sh
solr_uid=`id -u %{solr_user}`
if [ $? -ne 0 ]; then
  if [ "$distro" == "RedHat" ]; then
    adduser %{solr_user}
  elif [ "$distro" == "SUSE" ]; then
    useradd -m %{solr_user}
  else
    adduser --system --shell /bin/bash --group --disabled-password --home /home/%{solr_user} %{solr_user}
  fi
fi

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
* Wed Aug 26 2015 jks@sagevoice.com
- Inital version
