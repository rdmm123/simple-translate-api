FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

RUN apt update && apt upgrade
RUN apt install ffmpeg -y
RUN uvx playwright install --with-deps chromium

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=vendored/,target=vendored/ \
    uv sync --frozen --no-install-project --no-dev --group lambda

COPY pyproject.toml main.py uv.lock ./
COPY src ./src

RUN --mount=type=bind,source=vendored/,target=vendored/ \
    uv sync --frozen --no-dev --group lambda

FROM base as local_dev

WORKDIR /app

COPY vendored/aws-lambda-rie aws-lambda-rie
RUN chmod +x aws-lambda-rie

ENTRYPOINT ["./aws-lambda-rie", "python", "-m", "awslambdaric" ]
CMD ["main.handler"]