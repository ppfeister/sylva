# Installing Sylva the easy way

Sylva performs best as a Docker container, but several other methods are and will be supported in the future. The Docker images are all fully self-contained, which many users may find preferable.


## Docker

!!! tip
    The default image reflects the latest tagged release. To fetch the HEAD of `master`, use `ppfeister/sylva:preview`.

```bash
docker run --rm ppfeister/sylva sylva search <query> #(1)!
```

1.  Sylva can be found on both [Docker Hub][dockerhub]{:target="_blank"} and [GitHub Container Registry][ghcr]{:target="_blank"}.
    Users who prefer the latter can opt for `ghcr.io/ppfeister/sylva` instead.

```bash
# Alternatively...
docker run --rm -it ppfeister/sylva bash #(1)!
sylva search <query>
```

1.  Sylva can be found on both [Docker Hub][dockerhub]{:target="_blank"} and [GitHub Container Registry][ghcr]{:target="_blank"}.
    Users who prefer the latter can opt for `ghcr.io/ppfeister/sylva` instead.

___

## Docker Compose

```yaml
services:
  sylva:
    container_name: sylva
    image: 'ppfeister/sylva' #(1)!
```

1.  Sylva can be found on both [Docker Hub][dockerhub]{:target="_blank"} and [GitHub Container Registry][ghcr]{:target="_blank"}.
    Users who prefer the latter can opt for `ghcr.io/ppfeister/sylva` instead.

```bash
docker compose run --rm sylva sylva search <query>
```

___

## PyPI (pip)

!!! warning "You should know..."
    This method requires the installation of additional dependencies for full functionality.
    It is not fully self-contained.

    Basic functionality is still available.

```bash
pip install sylva
```

- Chrome or Chromium
- [xorg-x11-server-Xvfb]{:target="_blank"} (Fedora), [xvfb][xvfb-deb]{:target="_blank"} (Debian), or your distribution's equivalent

Without these two dependencies, Sylva will be unable to query targets that are behind a captcha.

[xorg-x11-server-Xvfb]: https://packages.fedoraproject.org/pkgs/xorg-x11-server/xorg-x11-server-Xvfb/
[xvfb-deb]: https://packages.debian.org/sid/xvfb
[dockerhub]: https://hub.docker.com/r/ppfeister/sylva
[ghcr]: https://github.com/ppfeister/sylva/pkgs/container/sylva

