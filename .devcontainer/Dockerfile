FROM mcr.microsoft.com/devcontainers/miniconda:1-3

WORKDIR /workspaces/boulder_examples
COPY environment.yml requirements.txt requirements-dev.txt ./
RUN conda env create -n boulder-examples -f environment.yml || conda env update -n boulder-examples -f environment.yml
SHELL ["conda", "run", "-n", "boulder-examples", "/bin/bash", "-c"]
