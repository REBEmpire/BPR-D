#!/bin/bash
set -e

# Export the key if provided, but ONLY if it's the correct one (ends in 809e)
if [ -n "$ABACUS_API_KEY" ]; then
    if [[ "$ABACUS_API_KEY" == *"809e" ]]; then
        export ABACUS_API_KEY=$ABACUS_API_KEY
        echo "Abacus API Key verified (ends in ...809e)."
    else
        echo "WARNING: ABACUS_API_KEY does not end in ...809e. It will NOT be exported to prevent using the wrong key."
        # Unset just in case
        unset ABACUS_API_KEY
    fi
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
