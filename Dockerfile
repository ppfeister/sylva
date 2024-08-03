FROM python:3.12-slim-bullseye AS cli-builder

# Repository information (for versioning)
COPY .git/ /app/.git/

# Source
COPY src/ /app/src/
COPY pyproject.toml /app/
COPY pdm.lock /app/

# Readme is needed to satisfy PyProject
COPY .github/README.md /app/.github/

# Testing source
COPY tests/ /app/tests/
COPY pytest.ini /app/
COPY tox.ini /app/

WORKDIR /app

# Extract version from git
RUN apt-get update
RUN apt-get install -y git
RUN apt-get clean

ARG REL_REF
RUN REL_REF=$(git describe --tags --abbrev=0)
RUN echo "Building $REL_REF"

# Build package
RUN pip install --upgrade pdm

ENV PDM_UPDATE_CHECK=false
ENV PDM_BUILD_SCM_VERSION=$REL_REF
RUN pdm install --check --prod --no-editable --verbose

# TODO Add unit tests

#####################################

FROM python:3.12-slim-bullseye AS cli

# Installation
COPY --from=cli-builder /app/.venv /app/.venv
COPY src/ /app/src/

# Documentation
COPY .github/README.md /app/
COPY LICENSE /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV SYLVA_ENV="docker"

CMD ["sylva"]
