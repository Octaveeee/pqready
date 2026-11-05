FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

CMD ["nginx", "-g", "daemon off;"]