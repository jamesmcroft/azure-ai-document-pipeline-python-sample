# Use a base image that supports Python.
FROM mcr.microsoft.com/vscode/devcontainers/python:1-3.11-bullseye

# Install Python dependencies
COPY ./src/AIDocumentPipeline/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
  && rm -rf /tmp/pip-tmp

# Install additional tools and dependencies
COPY ./.devcontainer/install-tools.sh /tmp/tools-tmp/
RUN chmod +x /tmp/tools-tmp/install-tools.sh \
  && /tmp/tools-tmp/install-tools.sh \
  && rm -rf /tmp/tools-tmp

# Default to bash shell
ENV SHELL=/bin/bash \
  DOCKER_BUILDKIT=1

# Mount for docker-in-docker
VOLUME [ "/var/lib/docker" ]
