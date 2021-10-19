# solr-rpm

## Introduction

RPM packaging instructions and scripts to package Solr server for
*enterprise* use.

## Usage

Code to build an RPM for Apache Solr 8.x.x+ on Red Hat and derivative OSes.

To use, first setup your development environment for docker or podman containers. 
Once that is done you can build an RPM by running something to this effect and retrieving the
artifact from `/tmp/solr-VERSION-rpm` on the final container.

    sudo docker build --network=dlan --build-arg="SOLR_X_Y_Z_VERSION=8.9.0" --build-arg="RPM_REL=2" -t deploymentdog/solr-rpm:centos7 -f Dockerfile .

Install the built RPM using

    sudo yum localinstall -y /path/to/solr.rpm

By default, the solr service is not started as the user might want to make
some changes to configs or cores. You can start the service as follows

    sudo systemctl start solr-server

And stop it using

    sudo systemctl stop solr-server

To allow solr to start on system startup, ensure you *enable* the service
    
    sudo systemctl enable solr-server

The `solr`, `post`, and `postlog` scripts are installed to `/usr/bin`, and are
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
2. Unlike the distribution, data lives in `/var/solr` so that you can have
configs completely separate from data. This will allow you to have data on
some other drive/partition, just by mounting it on `/var`. Upstream Solr
distribution tightly couples where cores' config and corresponding data live.
In more recent years, they have allowed for more flexibility in deployment, but
still, in general, require a tightly-coupled config or a highly customized one.
3. Constants/environment variables are defined in `/etc/solr/solr.in.sh`.
4. Binaries live in `/usr/share/solr` .
6. `solr` and `post` scripts are installed to `/usr/bin`.
Depending on your `PATH` variable, these scripts will be available after
installation as system wide commands on CLI.

## Notes for packagers

1. Constants defined at the top of spec file should tell you where most of
the things go.
2. SystemD service definition has placeholders defined (they start with `RPM_`)
that are replaced with constants from spec file. The same constants are
used to set values in `solr.in.sh`. This makes it easy to reorganize
installation while making us a little impervious to upstream changes.
3. This spec file only packages the `server`, `licenses`, `contrib`, and `bin` directories
from official Solr archive. The full distribution contains full javadocs in
HTML, bunch of plugins, distribution JARs and examples that are normally not
needed in enterprise deployments.
4. Code in this repo has been tested on CentOS 7 (2009) to package 8.9.x Solr.
Older versions are untested and unsupported. Please feel free to make
pull requests for bugs that you find. Ongoing support is not guaranteed.
5. I'll eventually mirror this to Docker hub when I have time for further ease of building.

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
