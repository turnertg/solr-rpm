# solr-rpm

## Introduction

RPM packaging instructions and scripts to package Solr server for
*enterprise* use.

## Usage

Code to build an RPM for Apache Solr 5.x.x+ on Red Hat and derivative OSes.

To use, first setup your development environment by running

    sudo ./setup.sh

Once that is done you can build an RPM by running

    ./build.sh 5.3.0 mycompany

Install the built RPM using

    sudo yum install -y /path/to/solr.rpm

By default, the solr service is not started as the user might want to make
some changes to configs or cores. It is, however, registered to automatically
start when the machine establishes network connection during boot. You can
start the service as follows

    sudo systemctl start solr-server

And stop it using

    sudo systemctl stop solr-server

The `solr` and `post` scripts are installed to `/usr/local/bin`, and are
expected to be available on CLI like any other application. For example, you
can check solr health using

    solr healthcheck -c <collection> -z <zkHost>

Although you can stop solr-server using `solr stop`, it is *NOT* recommended
because SystemD is configured to automatically restart the service and will
hence lead to undesired behavior.

If you want to conduct experiments, it will be better to start solr on any port
other than 8983 using `solr start`. See `solr --help` for details after
installation.

## Directory tree

1. All configs (except that of embeded Jetty), including cores,
lives in `/etc/solr`. No example cores are installed or configured.
2. Unlike the distribution, data lives in `/srv/solr` so that you can have
configs completely separate from data. This will allow you to have data on
some other drive/partition, just by mounting it on `/srv`. Upstream Solr
distribution tightly couples where cores' config and corresponding data live.
3. Constants/environment variables are defined in `/etc/default/solr.in.sh`.
4. SystemD definition is at `/lib/systemd/system/solr-server.service`.
5. Binaries live in `/usr/local/solr-<version>` with `/usr/local/solr`
pointing to it as a symlink.
6. `solr` and `post` scripts are installed to `/usr/local/bin`.
Depending on your `PATH` variable, these scripts will be available after
installation as system wide commands on CLI.

## Notes for packagers

1. Constants defined at the top of spec file should tell you where most of
the things go.
2. SystemD service definition has placeholders defined (they start with `RPM_`)
that are replaced with constants from spec file. The same constants are
used to set values in `solr.in.sh`. This makes it easy to reorganize
installation while making us a little impervious to upstream changes.
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
6. Does not adhere to best practices. Some refactoring is needed. See:
    - https://fedoraproject.org/wiki/Packaging:Java?rd=Packaging/Java
    - https://fedoraproject.org/wiki/Packaging:Scriptlets?rd=Packaging:ScriptletSnippets

## License

Although the code has deviated significantly from original repo, the copyright
notices have been preserved wherever they appeared. Same license applies for
code in this repo too.

### Original notice

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
