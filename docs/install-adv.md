# Installing Sylva the hard way

Installing Sylva from source has __zero__ official support for end users. We only
recommend this method for advanced users or those who plan to contribute to the
project.

For the purposes of this document, it is assumed that the user is running Linux.

## Overview

Sylva uses a [PDM]{:target="_blank"} backend. There is no `requirements.txt` file, and Issues should
__not__ be raised for this missing file.

## Prerequisites

- [Install PDM according to their documentation][pdm-install]{:target="_blank"}
- Chrome or Chromium
- [xorg-x11-server-Xvfb][xvfb-fed]{:target="_blank"} (Fedora), [xvfb][xvfb-deb]{:target="_blank"} (Debian), or your distribution's equivalent

[xvfb-fed]: https://packages.fedoraproject.org/pkgs/xorg-x11-server/xorg-x11-server-Xvfb/
[xvfb-deb]: https://packages.debian.org/sid/xvfb

## Installing Sylva for development

```bash
git clone https://github.com/ppfeister/sylva.git
cd sylva
pdm install -G:all
```

Sylva is now installed in an isolated live environment. Changes made to the code should be reflected
within this environment immediately.

All dependency groups are installed, including those for regression testing, MkDocs editing, etc.

#### Running within the venv

Users can enter the virtual environment by running `source .venv/bin/activate`. The difficulty here
is that global installs of the same package are known to interfere. If you have Sylva installed
globally as well, you should defer to the next method.

Assuming you have entered the venv, you can run Sylva as you would normally.

#### Running via PDM

Due to the aforementioned complication, many developers may opt to run Sylva through PDM itself.

```bash
pdm run sylva search <query>
```

## Installing Sylva globally

!!! warning
    This is __not__ an officially supported method of installation.
    
    This method also lacks any means of automatic or assisted updates.

```bash
git clone https://github.com/ppfeister/sylva.git
cd sylva
pdm install --global --prod
```

## Building the Docker image

Sylva provides both the latest release (semver tagged and as latest) and the current state of
`master` (as preview) as a Docker image, available on both [Docker Hub][dockerhub]{:target="_blank"}
and the [GitHub Container Registry][ghcr]{:target="_blank"}.

If you'd rather build your own image, such as for development use or validation, you can do so with
the provided multi-stage [Dockerfile]{:target="_blank"}. The prerequisites mentioned earlier can be
skipped you're *only* building the Docker image.

Build target `cli-prod` is the standard command line target. Future targets may include web
interfaces, or other added functionality.

```bash
git clone https://github.com/ppfeister/sylva.git
cd sylva
docker build --target cli-prod -t ppfeister/sylva .
```


[PDM]: https://pdm-project.org
[pdm-install]: https://pdm-project.org/en/latest/#installation
[dockerhub]: https://hub.docker.com/r/ppfeister/sylva
[ghcr]: https://github.com/ppfeister/sylva/pkgs/container/sylva
[semver]: https://semver.org
[Dockerfile]: https://github.com/ppfeister/sylva/blob/master/Dockerfile
