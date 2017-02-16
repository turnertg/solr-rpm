# solr-rpm

## Introduction

RPM packaging instructions and scripts to package Solr server.

## Usage

Code to build an RPM for Apache Solr 5.x.x+ on Red Hat and derivative OSes.

To use, first setup your development environment by running

    sudo ./setup.sh

Once that is done you can build an RPM by running

    ./build.sh 5.3.0 mycompany

## Notes for packagers

1. Constants defined at the top of spec file should tell you where most of 
the things go.
2. SystemD service definition has placeholders defined (they start with RPM_) 
that are replaced with constants defined in spec file. The same constants are
used to put values in `solr.in.sh`. This makes it easy to reorganize
installation without figuring out what patches are supposed to do, and also
make us a little impervious to upstream changes.
3. This spec file only packages the `server`, `licenses` and `bin` directories 
from official Solr archive. The full distribution contains full javadocs in 
HTML, bunch of plugins, distribution JARs and examples that are normally not 
needed in enterprise deployments.
4. Code in this repo has been tested on CentOS 7.3 to package 6.4.x Solr.
Packaging 5.x.x should work, but has not been tested. Please feel free to make
pull requests for bugs that you find. Ongoing support is not guaranteed.
5. The spec file currently puts Java 1.8 in dependencies. If you are packaging
older versions, it might be better to change that to whatever is applicable
for that release.

Copyright © 2015 Jason Stafford

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

> [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
