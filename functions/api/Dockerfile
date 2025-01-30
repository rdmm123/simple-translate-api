FROM public.ecr.aws/lambda/python:3.13 AS builder

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PROJECT_ENVIRONMENT="/var/lang/"

WORKDIR /app

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=vendored/,target=vendored/ \
    uv sync --frozen --no-install-project --no-dev --extra api --extra telegram --extra lambda

COPY pyproject.toml main.py uv.lock ./
COPY src ./src
COPY functions/api/handler.py ./handler.py

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=vendored/,target=vendored/ \
    uv sync --frozen --no-dev --extra api --extra telegram --extra lambda

FROM public.ecr.aws/lambda/python:3.13

COPY --from=builder /app /var/task
COPY --from=builder /var/lang /var/lang

CMD ["handler.handler"]