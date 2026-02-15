#!/bin/bash
set -e

# Export the key if provided
if [ -n "$ABACUS_API_KEY" ]; then
    export ABACUS_API_KEY=$ABACUS_API_KEY
fi

# Set workspace
if [ -n "$WORKSPACE_DIR" ]; then
    mkdir -p "$WORKSPACE_DIR"
    cd "$WORKSPACE_DIR"
fi

# Start tmux server and session explicitly
echo "Starting tmux session..."
tmux new-session -d -s agent || echo "Tmux session already exists"

# Change back to /app
cd /app

echo "Starting Agent Bridge for Deep Agent..."
exec uvicorn shared.agent_bridge:app --host 0.0.0.0 --port 8000
