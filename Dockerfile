# This Dockerfile to serve as a temporary solution for the Chromium 127 crash issue

FROM python:3.12-slim-bookworm AS cli-builder

# Repository information (for versioning)
COPY .git/ /app/.git/

# Source
COPY src/ /app/src/
COPY pyproject.toml pdm.lock /app/

# No idea why symlinks refuse to work when dockerized but here we are
RUN rm /app/src/sylva/helpers/flaresolverr /app/src/sylva/helpers/pgpy
RUN mv /app/src/flaresolverr/src/flaresolverr/ /app/src/sylva/helpers/flaresolverr
RUN mv /app/src/pgpy/pgpy/ /app/src/sylva/helpers/pgpy
RUN rm -rf /app/src/flaresolverr

# Readme is needed to satisfy PyProject
COPY .github/README.md /app/.github/

# Testing source
COPY tests/ /app/tests/
COPY tox.ini pytest.ini /app/

WORKDIR /app

# Extract version from git
RUN apt-get update
RUN apt-get install -y --no-install-recommends git
RUN apt-get clean

ARG REL_REF
RUN REL_REF=$(git describe --tags --abbrev=0)
RUN echo "Building $REL_REF"

# Build package
RUN pip install --upgrade pdm

ENV PDM_UPDATE_CHECK=false
ENV PDM_BUILD_SCM_VERSION=$REL_REF
RUN pdm install --check --prod --no-editable --frozen-lockfile --verbose

#####################################

FROM alexfozor/flaresolverr@sha256:3e5e1335c31365b5b0d9a737097c6a719de0ba49fed7db65cd828d75ae1bbecb AS cli-prod

# Installation
COPY --from=cli-builder /app/.venv /app/.venv
COPY src/ /app/src/

# Documentation
COPY .github/README.md COPYING CREDITS /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV SYLVA_ENV="docker"

ENTRYPOINT ["/usr/bin/dumb-init", "--", "sylva"]

CMD ["sylva"]
