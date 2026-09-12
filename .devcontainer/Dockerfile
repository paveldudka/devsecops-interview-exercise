FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ARG UV_VERSION=0.8.15
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

ENV UV_LINK_MODE=copy
