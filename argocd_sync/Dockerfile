FROM python:3.12-slim

# Build arg: set to "true" to include gws (Google Workspace CLI) via Node.js.
# Build for gws mode:  docker build --build-arg INSTALL_GWS=true ...
ARG INSTALL_GWS=false

WORKDIR /app

# Python dependencies (always installed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# gws CLI — only when INSTALL_GWS=true to keep the local-mode image lean.
# Node LTS is pulled from Debian's nodesource; npm is included.
RUN if [ "$INSTALL_GWS" = "true" ]; then \
      apt-get update && \
      apt-get install -y --no-install-recommends curl gnupg && \
      curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
      apt-get install -y --no-install-recommends nodejs && \
      npm install -g @googleworkspace/cli && \
      apt-get purge -y curl gnupg && \
      apt-get autoremove -y && \
      apt-get clean && \
      rm -rf /var/lib/apt/lists/* /root/.npm; \
    fi

COPY fetch.py upsert.py sync.sh requirements.txt ./
COPY output/ output/

RUN chmod +x sync.sh

ENTRYPOINT ["./sync.sh"]
