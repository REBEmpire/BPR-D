#!/bin/bash
set -e

# Export the key if provided
if [ -n "$JULES_API_KEY" ]; then
    export CODEBUFF_API_KEY=$JULES_API_KEY
    export JULES_LEGACY_KEY=$JULES_API_KEY
fi

# Start tmux server and session explicitly
echo "Starting tmux session..."
tmux new-session -d -s agent || echo "Tmux session already exists"

echo "Starting Agent Bridge for Jules..."
exec uvicorn shared.agent_bridge:app --host 0.0.0.0 --port 8000
