FROM docker.io/library/python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /bin/uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Build the executable
RUN apt-get update \
 && apt-get install -y binutils
RUN uv run pyinstaller --onefile --name vtr vscode_task_runner/__main__.py \
 && chmod +x dist/vtr \
 && cp dist/vtr dist/vscode-task-runner

# Create a minimal distroless image with the executable
FROM scratch

# Copy the executable from the builder stage
COPY --from=builder /app/dist/vtr /app/dist/vscode-task-runner /
WORKDIR /io

# Set the entrypoint to the executable
ENTRYPOINT ["/vtr"]