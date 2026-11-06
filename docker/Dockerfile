FROM debian:trixie-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
    ca-certificates \
    python3 \
    && rm -rf /var/lib/apt/lists/*

