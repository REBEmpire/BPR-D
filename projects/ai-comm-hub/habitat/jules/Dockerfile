FROM node:20-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y     python3     python3-pip     python3-venv     tmux     curl     git     && rm -rf /var/lib/apt/lists/*

# Install Codebuff
RUN npm install -g codebuff

# Set up environment
WORKDIR /app
ENV PATH="/app/venv/bin:/home/jules/.nvm/versions/node/v22.22.0/bin:/home/jules/.pyenv/shims:/home/jules/.pyenv/bin:/home/jules/.local/bin:/opt/flutter/bin:/usr/lib/dotnet:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:/go/bin:/usr/local/go/bin:/usr/share/gradle/bin:/usr/share/maven/bin:/home/jules/.local/bin:/home/jules/.cargo/bin:/usr/local/bun/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin:/home/jules/.dotnet/tools"

# Create Python virtual environment for the bridge
RUN python3 -m venv /app/venv

# Install Python dependencies for the bridge
COPY shared/requirements.txt /app/shared/requirements.txt
RUN pip install --no-cache-dir -r /app/shared/requirements.txt

# Copy bridge code
COPY shared/agent_bridge.py /app/shared/agent_bridge.py

# Copy entrypoint script
COPY jules/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Environment variables will be injected by Docker Compose
# JULES_API_KEY
# ABACUS_API_KEY (not needed here but good to know)

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
