FROM python:3.12-slim-bookworm AS cli-builder

# Repository information (for versioning)
COPY .git/ /app/.git/

# Source
COPY src/ /app/src/
COPY pyproject.toml pdm.lock /app/

# No idea why symlinks refuse to work when dockerized but here we are
RUN rm /app/src/sylva/helpers/flaresolverr
RUN mv /app/src/flaresolverr/src/flaresolverr/ /app/src/sylva/helpers/flaresolverr
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

# TODO Add unit tests

#####################################

FROM python:3.12-slim-bookworm AS cli-prod

# Dependencies not found in package
RUN apt-get update
RUN apt-get install -y --no-install-recommends chromium chromium-driver xvfb dumb-init
RUN apt-get clean

# Remove temporary files and hardware decoding libraries
RUN rm -rf /var/lib/apt/lists/* \
  && rm -f /usr/lib/x86_64-linux-gnu/libmfxhw* \
  && rm -f /usr/lib/x86_64-linux-gnu/mfx/*

RUN useradd --home-dir /app --create-home --shell /bin/bash sylva \
  && chown -R sylva:sylva /app

USER sylva

# Installation
COPY --from=cli-builder /app/.venv /app/.venv
COPY src/ /app/src/

# Documentation
COPY .github/README.md COPYING CREDITS /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV SYLVA_ENV="docker"

ENTRYPOINT ["/usr/bin/dumb-init", "--", "sylva"]

CMD ["sylva"]
