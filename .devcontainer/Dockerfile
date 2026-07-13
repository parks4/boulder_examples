FROM mcr.microsoft.com/devcontainers/miniconda:1-3

WORKDIR /workspaces/boulder_examples
COPY environment.yml requirements.txt requirements-dev.txt ./
RUN conda env create -n boulder -f environment.yml || conda env update -n boulder -f environment.yml
SHELL ["conda", "run", "-n", "boulder", "/bin/bash", "-c"]

# Put the env's bin dir on PATH for every process in the container (VS Code's
# integrated terminal, `docker exec`, postAttachCommand, ...) — not just
# shells that source .bashrc — so `boulder` and friends work without an
# explicit `conda activate` in every new terminal.
ENV PATH="/opt/conda/envs/boulder/bin:${PATH}"
