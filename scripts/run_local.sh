#!/bin/bash
# Reads OPENAI_API_KEY from macOS Keychain, runs MCP server from local source
export OPENAI_API_KEY=$(security find-generic-password -s "OPENAI_API_KEY" -a "glassbox-ai" -w)
cd /Users/sourabh/Documents/projects/glassbox-ai/src
exec /Users/sourabh/opt/anaconda3/envs/glassbox_311/bin/python -m glassbox.server
