FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Persistent data (database) should be mounted at /data
ENV DATABASE_PATH=/data/tdsm.db

ENTRYPOINT ["tdsm"]
