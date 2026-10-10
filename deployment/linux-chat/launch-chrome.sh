#!/bin/sh
# Wait for X before opening the manual ChatGPT window. No model calls or prompts.
set -eu
attempt=0
until xdpyinfo >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then
        exit 1
    fi
    sleep 1
done
exec /usr/bin/google-chrome --user-data-dir=/home/seluser/ebt-profile --remote-debugging-port=9222 --no-first-run --start-maximized https://chatgpt.com/
