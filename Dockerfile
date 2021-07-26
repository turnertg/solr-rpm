# Copyright © 2021 Trevor Turner
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

#
# base image
#

FROM centos:7 AS base
MAINTAINER turnertg

# setup
RUN yum install -y rpm-build tar wget openssl coreutils

#
# builder image
#

FROM base AS builder

ARG SOLR_X_Y_Z_VERSION
ARG RPM_REL

# rpmbuild command recommends to use `builder:builder` as user:group.
RUN useradd -u 1000 builder

RUN mkdir -p /home/builder/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
RUN mkdir -p /home/builder/solr-rpm
RUN chown -R builder:builder /home/builder/rpmbuild
RUN chown -R builder:builder /home/builder/solr-rpm

WORKDIR /home/builder/solr-rpm
USER builder

COPY . /home/builder/solr-rpm/
RUN /home/builder/solr-rpm/scripts/build.sh $SOLR_X_Y_Z_VERSION $RPM_REL

#
# tester image
#

#FROM base AS tester

#ARG RUBY_X_Y_VERSION

#COPY --from=builder /tmp/ruby-$RUBY_X_Y_VERSION-rpm /tmp/ruby-$RUBY_X_Y_VERSION-rpm
#RUN yum install -y /tmp/ruby-$RUBY_X_Y_VERSION-rpm/ruby-$RUBY_X_Y_VERSION.*.$(uname -m).rpm

# test for passenger dependency checks
#RUN yum install -y pygpgme curl epel-release yum-utils
#RUN yum-config-manager --enable epel
#RUN curl --fail -sSLo /etc/yum.repos.d/passenger.repo https://oss-binaries.phusionpassenger.com/yum/definitions/el-passenger.repo
#RUN yum update -y
#RUN yum install -y mod_passenger
