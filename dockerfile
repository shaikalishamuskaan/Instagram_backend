FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

COPY src ./src

RUN uv sync --frozen

COPY . .

ENV PYTHONPATH=/app/src

CMD ["uv", "run", "python", "-m", "dbms.cli"]