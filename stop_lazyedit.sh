#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
if [ -f "$SCRIPT_DIR/lazyedit_config.sh" ]; then
    source "$SCRIPT_DIR/lazyedit_config.sh"
fi

SESSION_NAME="${SESSION_NAME:-lazyedit}"

tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
tmux kill-session -t "la-lazyedit" 2>/dev/null || true
